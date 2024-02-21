#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/13 2:32 PM
# @Author  : baluobo
# @File    : chatglm3.py
# @Description :
import pymysql
import requests
import json
import pandas as pd
from table_schema import database_schema_string,ngfa_database_schema_string#,ngfa_table_schema
from generate_ngfa_sql import prepocess,generate_settlement_sql
from func_tool import functions_draw_bar,draw_pic
import sqlparse

def get_db_data(sql):
    conn = pymysql.connect(host='192.168.36.198',
                           user='root',
                           passwd='Trendy@2022',
                           #db='ngfa',
                           port=3306)  # 和mysql服务端设置格式一样（还可设置为gbk, gb2312）
    df = pd.read_sql_query(sql, conn)
    return df

# 其中根据省份的拼音首字母大写作为省份筛选条件，源端省份使用srcProvinceCode，目标省份使用dstProvinceCode，路由省份与源端省份相同；
#                     流量类型根据表结构中的枚举进行转换，源端类型通过srcType筛选，目标端类型通过dstType筛选；
#                     当源省份和目标省份不同时，通过上行口出端口统计，通过outInterfaceType筛选；当源省份和目标省份相同时，走下行口的入端口进行统计，通过inInterfaceType筛选；
#                     时间通过timestamp进行筛选。
#                     返回的查询SQL包装在json中，且SQL需要满足MYSQL数据库的语法。
functions = [{
        "name": "text_convert",
        "description": f"该方法用于解析用户的问题，将用户的提问分解为源端省份编码、目标省份编码、源端类型、目标类型、开始时间、结束时间"
                       f"例1从安徽城域网流入浙江IDC的均值流量，其中源端省份为安徽，源端类型城域网，目标省份为浙江，目标类型为IDC；"
                       f"例2从安徽城域网+IDC流入浙江IDC的均值流量，其中源端省份为安徽，源端类型城域网+IDC，目标省份为浙江，目标类型为IDC；"
                       f"例3从安徽城域网流入浙江的均值流量，其中源端省份为安徽，源端类型城域网，目标省份为浙江，目标类型为''；"
                       f"例4从安徽城域网流出的均值流量，其中源端省份为安徽，源端类型城域网，目标省份为''，目标类型为''；"
                       f"例5从北京IDC+WLW流入31省及云公司的均值流量，其中源端省份为北京，源端类型为'IDC+WLW'，目标省份为全国，目标类型为''；"
                       f"例6从31省及云公司流入北京的均值流量，其中源端省份为全国，源端类型为''，目标省份为北京，目标类型为''；"
                       f"例7北京所有类型在2023-12-18 00:00:00至2023-12-18 12:00:00时间区间内流入31省及云公司的均值流量速率(单位:Gbps)，其中源端省份为北京，源端类型为''，目标省份为全国，目标类型为''；"
                       f"例8北京IDC流入31省及云公司的均值流量速率(单位:Gbps)，其中源端省份为北京，源端类型为IDC，目标省份为全国，目标类型为''；"
                       f"例9北京所有类型流入31省及云公司IDC的均值流量速率(单位:Gbps)，其中源端省份为北京，源端类型为''，目标省份为全国，目标类型为IDC；"
                       f"例10浙江WLW和IDC流入江苏IDC的均值流量(单位Gbps)，其中源端省份为'安徽'，源端类型'WLW+IDC'，目标省份为'江苏'，目标类型为IDC；"
                       f"例11江苏WLW和IDC流入江苏IDC的均值流量(单位Gbps)，其中源端省份为'江苏'，源端类型'WLW+IDC'，目标省份为'江苏'，目标类型为IDC；"
                       f"例12查询流入安徽城域网的均值流量，其中源端省份为''，源端类型''，目标省份为'安徽'，目标类型为城域网；"
    ,
        "parameters": {
            "type": "array",
            "properties": {
                "srcProvince": {
                        "type": "String",
                        "description": "源端省份，只输出省、直辖市、自治区的名称，例北京"
                },
                "dstProvince": {
                        "type": "String",
                        "description": "目标省份，只输出省、直辖市、自治区的名称，例北京"
                },
                "srcType": {
                        "type": "String",
                        "description": "源端类型，一般出现在源端省份后,当出现多个时，用+连接，若没有指定，则返回''"
                },
                "dstType": {
                        "type": "String",
                        "description": "目标类型，一般出现在目标省份后，当出现多个时，用+连接，若没有指定，则返回''"
                },
                "routerProvince": {
                        "type": "String",
                        "description": "路由省份，当输入中存在'从某某省份设备上看'，即该省份为路由省份，例从江苏设备上看，则输出江苏；若用户输入没有设定，则输出与源端省份输出相同"
                },
                "startTime": {
                        "type": "String",
                        "description": "开始时间，如果输入的时间描述为昨日或者今日等，请根据系统当前的时间和日期转换，输出的格式为YYYY-MM-DD HH:mm:ss,例2023-12-10 00:00:00"
                },
                "endTime": {
                        "type": "String",
                        "description": "结束时间，如果输入的时间描述为昨日或者今日等，请根据系统当前的时间和日期转换，输出的格式为YYYY-MM-DD HH:mm:ss,例2023-12-10 00:00:00"
                }
            },
            "required": ["srcProvince","dstProvince","srcType","dstType","routerProvince","startTime","endTime"],
        },
    }]
def create_chat_completion(model, messages, functions, use_stream=False):
    base_url = "http://172.16.16.99:8020"
    if functions == None:
        data = {
            #"functions": functions,  # 函数定义
            "model": model,  # 模型名称
            "messages": messages,  # 会话历史
            "stream": use_stream,  # 是否流式响应
            "max_tokens": 1000,  # 最多生成字数
            "temperature": 0.8,  # 温度
            "top_p": 0.8,  # 采样概率
        }
    else:
        data = {
            "functions": functions,  # 函数定义
            "model": model,  # 模型名称
            "messages": messages,  # 会话历史
            "stream": use_stream,  # 是否流式响应
            "max_tokens": 1000,  # 最多生成字数
            "temperature": 0.8,  # 温度
            "top_p": 0.8,  # 采样概率
        }

    response = requests.post(f"{base_url}/v1/chat/completions", json=data, stream=use_stream)
    if response.status_code == 200:
        #print(use_stream)
        if use_stream:
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')[6:]
                    try:
                        response_json = json.loads(decoded_line)
                        content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        print(content)
                    except:
                        print("Special Token:", decoded_line)
        else:
            # 处理非流式响应
            decoded_line = response.json()
            #print(decoded_line)
            content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
            #print(f'你的回答是{content}')
            if functions != None:
                print(f'content:{content}')
                mid_result = content.split('tool_call')[1].replace("```","")
                #print(mid_result)
                return mid_result
            else:
                return content
    else:
        print("Error:", response.status_code)
        return None
def prompt_check(prompt,use_stream=False):
    #chat_messages = [
    result = create_chat_completion("chatglm3-6b", messages=prompt, functions=None, use_stream=use_stream)
    return result

def function_chat(prompt,use_stream=False):
    print("function call",prompt)
    # chat_messages = [
    #     {"role": "user", "content": f'{prompt}'}
    # ]
    try:
        result = create_chat_completion("chatglm3-6b", messages=prompt, functions=functions, use_stream=use_stream)
        print(f'result:{result},{type(result)}')
        #sql_input = f'根据条件{result}生成SQL'
        re = prepocess(result)
    except:
        re = None
    print(f're:{re}')
    if re == None:
        return False, False
    if re['startTime'] == '' or re['endTime'] == '':
        return False,False
    else:
        sql = generate_settlement_sql(re)
        print(f'原始sql:{sql}')
        sql = sql.replace('\n',' ').replace(',)',')')
        data = get_db_data(sql)
        # chat_messages = [
        #     # session,
        #     {"role": "user", "content": f"请帮我美化一下{sql}，对SQL内容不进行修改"}
        # ]
        # formatted_sql = create_chat_completion("chatglm3-6b", messages=chat_messages, functions=None, use_stream=use_stream)
        # print(f'转换后的SQL:{formatted_sql}')
        return sql,data

    # chat_messages = [
    #     session,
    #     {"role": "user", "content": sql_input}
    # ]
    # sql = create_chat_completion("chatglm3-6b", messages=chat_messages, functions=None, use_stream=use_stream)
    # print(f'sql:{sql}')
    # return sql

def draw_bar(data,use_stream=False):
    # data = data.to_dict('list')
    # chat_messages = [
    #     {"role": "system", "content":f'将输入的数据整理城画柱状图所需要的数据'},
    #     {"role": "user", "content":f'根据{data}数据返回绘图数据'}
    # ]
    # content = create_chat_completion("chatglm3-6b", messages=chat_messages, functions=functions_draw_bar, use_stream=use_stream)
    # c = content.replace('(', "{").replace(')', "}").replace('=', ":").replace("'", '"').replace('xAxis', '"xAxis"').replace(
    #     'yAxis', '"yAxis"').replace('x_name', '"x_name"').replace('y_name', '"y_name"')
    # c = json.loads(c)
    # bar = draw_pic(c['xAxis'], c['yAxis'],c['x_name'], c['y_name'])
    data['x_axis'] = data['srcProvinceCode'] + '-->' +data['dstProvinceCode']
    data = data.to_dict('list')
    bar = draw_pic(data['x_axis'], data['rate'], "", "flow")
    return bar
if __name__ == '__main__':
    dict = {'srcProvinceCode,': ['JS','JS','JS','JS'], 'dstProvinceCode,': ['JS','BJ','ZJ','AH'],'flow':[1000,2340,342,34121]}
    # b = draw_bar(dict)
    # #c = prepocess(b)
    # c = b.replace('(', "{").replace(')', "}").replace('=', ":").replace("'", '"').replace('xAxis', '"xAxis"').replace(
    #     'yAxis', '"yAxis"').replace('x_name', '"x_name"').replace('y_name', '"y_name"')
    # c = json.loads(c)
    # print(type(c))
    # draw_pic(c['xAxis'], c['yAxis'],c['x_name'], c['y_name'])

    a = pd.DataFrame(dict)
    print(a)
    b = a.to_dict('list')
    print(b)
