#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/13 2:32 PM
# @Author  : baluobo
# @File    : chatglm3.py
# @Description :
import requests
import json
from table_schema import database_schema_string,ngfa_database_schema_string#,ngfa_table_schema
from generate_ngfa_sql import prepocess,generate_settlement_sql
from prompt1 import few_shot
from prompt2 import session

# 其中根据省份的拼音首字母大写作为省份筛选条件，源端省份使用srcProvinceCode，目标省份使用dstProvinceCode，路由省份与源端省份相同；
#                     流量类型根据表结构中的枚举进行转换，源端类型通过srcType筛选，目标端类型通过dstType筛选；
#                     当源省份和目标省份不同时，通过上行口出端口统计，通过outInterfaceType筛选；当源省份和目标省份相同时，走下行口的入端口进行统计，通过inInterfaceType筛选；
#                     时间通过timestamp进行筛选。
#                     返回的查询SQL包装在json中，且SQL需要满足MYSQL数据库的语法。

functions = [{
        "name": "text_convert",
        "description": f"该方法用于解析用户的问题，将用户的提问分解为源端省份编码、目标省份编码、源端类型、目标类型、开始时间、结束时间"
                       f"其中解析需要依据如下表结构{ngfa_database_schema_string}"
                       f"例1从安徽城域网流入浙江IDC的均值流量，其中源端省份为安徽，源端类型城域网，目标省份为浙江，目标类型为IDC；"
                       f"例2从安徽城域网+IDC流入浙江IDC的均值流量，其中源端省份为安徽，源端类型城域网+IDC，目标省份为浙江，目标类型为IDC；",
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
                "interfaceType": {
                        "type": "String",
                        "description": "当路由省份等于源端省份，输出为'出端口的上行口';当"
                },

                "startTime": {
                        "type": "String",
                        "description": "开始时间"
                },
                "endTime": {
                        "type": "String",
                        "description": "结束时间"
                }
            },
            "required": ["srcProvince","dstProvince","srcType","dstType","routerProvince","startTime","endTime"],
        },
    }]

def create_chat_completion(model, messages, functions, use_stream=False):
    base_url = "http://172.16.16.99:8000"
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
        print(use_stream)
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
                mid_result = content.split('tool_call')[1].replace("```","")
                #print(mid_result)
                return mid_result
            else:
                return content
    else:
        print("Error:", response.status_code)
        return None

def function_chat(prompt,use_stream=False):
    chat_messages = [
        #session,
        {"role": "user", "content": prompt}
    ]
    result = create_chat_completion("chatglm3-6b", messages=chat_messages, functions=functions, use_stream=use_stream)
    print(f'result:{result},{type(result)}')
    #sql_input = f'根据条件{result}生成SQL'
    re = prepocess(result)
    print(re)
    sql = generate_settlement_sql(re)
    print(sql)
    # chat_messages = [
    #     session,
    #     {"role": "user", "content": sql_input}
    # ]
    # sql = create_chat_completion("chatglm3-6b", messages=chat_messages, functions=None, use_stream=use_stream)
    # print(f'sql:{sql}')
    # return sql


if __name__ == '__main__':
    while (1):
        a = input("请输入：")
        function_chat(a)