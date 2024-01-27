#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/26 2:20 PM
# @Author  : baluobo
# @File    : generate_ngfa_sql.py
# @Description :

import arrow
import json
from datetime import datetime

type_dict = {'IDC':'1','城域网':'2','IDC客户':'3','中国移动':'4','中国联通':'5','DNS':'6','ITV':'7','NOC':'8',
             'PT':'9','QXZX':'10','SOC':'11','SW':'12','WG':'13','WLW':'14','DX-YD':'15','MAN':'2'}

provience_dict = {'海南': 'HI', '江苏': 'JS', '宁夏': 'NX', '安徽': 'AH', '重庆': 'CQ', '甘肃': 'GS', '黑龙江': 'HL', '吉林': 'JL',
                  '辽宁': 'LN', '贵州': 'GZ', '新疆': 'XJ', '西藏': 'XZ', '云南': 'YN', '福建': 'FJ', '青海': 'QH', '四川': 'SC',
                  '上海': 'SH', '广西': 'GX', '陕西': 'SN', '北京': 'BJ', '河南': 'HA', '山西': 'SX', '广东': 'GD', '湖北': 'HB',
                  '江西': 'JX', '河北': 'HE', '湖南': 'HN', '内蒙古': 'NM', '山东': 'SD', '天津': 'TJ', '浙江': 'ZJ','全国':('LT','YD','WG','DNS','')}

import difflib

def calculate_similarity(str1, str2):
    similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
    return similarity

def prepocess(function_result):
    '''

    :param function_result:
    :return:
    '''
    function_result = function_result.replace("(","").replace(")","")
    #json_result = json.loads(function_result)
    condition = function_result.split(',')
    condition_dict={}
    for con in condition:
        con_list = con.split('=')
        condition_dict[con_list[0].replace(' ','')] = con_list[1].replace("'",'').replace('\n','')
    return condition_dict

def generate_provience(condition):
    '''
    根据输出的省份进行转换，不区分源端、目标端、路由端
    :param condition:目前只能处理单一省份或者用加号连接的多个省份，比如安徽、安徽+江苏
    :return:
    '''
    condition_tuple = ()
    # 当时加号连接的多个省份时，则输出tuple
    if "+" in condition:
        condition_list = condition.split("+")
        for con in condition_list:
            con = con.replace("'")
            condition_tuple += (provience_dict[con],)
        provience_condition = condition_tuple
    elif condition == '全国':
        provience_condition = provience_dict[condition]
    # 否则输出单个或者不指定目标省份
    else:
        try:
            condition = condition.replace("'",'')
            condition_tuple += (provience_dict[condition],)
            provience_condition = condition_tuple
        except Exception as e:
            print(e)
            provience_condition = ''
    return provience_condition

def generate_type(condition):
    '''
    根据输入的网络类型进行匹配，不区分源端和目标端
    :param condition:网络类型，比如IDC或者IDC+WLW，只默认这两种格式
    :return:
    '''
    condition_tuple = ()
    # 当为空时，可能是prompt未指定，则不生成筛选条件，返回空
    if condition == "":
        type_condition = ''
    # 当存在多个网络类型时，则输出tuple
    elif '+' in condition:
        condition_list = condition.split("+")
        for con in condition_list:
            condition_tuple += (type_dict[con],)
        type_condition = condition_tuple
    # 其他
    else:
        try:
            # 单一的筛选条件
            type_condition = type_dict[condition]
            condition_tuple += (type_condition,)
            type_condition = condition_tuple
        except Exception as e:
            print(e)
            # 出现其他情况，暂定为空
            type_condition = ''

    return type_condition

def generate_interface(condition):
    '''
    通过源端、目标端、路由省份之间的关系，确定统计的接口类型
    :param condition:CHATGLM3 funcion call 的输出{'srcProvince': "'安徽'", 'dstProvince': "'江苏'", 'srcType': "'城域网+IDC'", 'dstType': "'城域网+IDC'", 'routerProvince': "'安徽'", 'startTime': "'2023-12-18 00:00:00'", 'endTime': "'2023-12-18 12:00:00'"}
    :return:
    '''
    print(condition['srcProvince'],condition['dstProvince'],condition['routerProvince'])
    # 源端省份与目标省份相同，从入接口的下行口统计
    if condition['srcProvince'] == condition['dstProvince']:
        interface_condition = "inInterfaceType = 'dt'"
    # 当路由省份为空，且目标省份和源端省份不同，默认走源端路由出发，因此从出端口的上行口统计
    elif condition['routerProvince'] == '' or condition['srcProvince'] == condition['routerProvince']:
        interface_condition = "outInterfaceType = 'ut'"
    # 当目标省份与路由省份相同，则是从目标端进行统计，则是从进口的上行口进行统计
    elif condition['dstProvince'] == condition['routerProvince']:
        interface_condition = "inInterfaceType = 'ut'"
    # 其他条件，则默认从出端口的上行口统计，也就是默认从源端角度去看
    else:
        interface_condition = "outInterfaceType = 'ut'"
    return interface_condition

def generate_time_diff_hour(st,et):
    '''
    计算开始时间和结束时间之间的小时差
    :param st:开始时间
    :param et:结束时间
    :return:
    '''
    st = arrow.get(st).format('YYYY-MM-DD HH:mm:ss')
    et = arrow.get(et).format('YYYY-MM-DD HH:mm:ss')
    startTime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
    endTime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S")
    hour_diff = (endTime - startTime).total_seconds() / 60 / 60
    #print("两个时间相差{}小时".format(int(hour_diff)))
    return abs(hour_diff)

def generate_settlement_sql(input):
    '''
    根据funcion call的输出拼装出SQL
    :param input:CHATGLM3 funcion call 的输出{'srcProvince': "'安徽'", 'dstProvince': "'江苏'", 'srcType': "'城域网+IDC'", 'dstType': "'城域网+IDC'", 'routerProvince': "'安徽'", 'startTime': "'2023-12-18 00:00:00'", 'endTime': "'2023-12-18 12:00:00'"}
    :return:
    '''
    # 这些是必须要有的
    ST = arrow.get(input['startTime']).format('YYYY-MM-DD HH:mm:ss')
    ET = arrow.get(input['endTime']).format('YYYY-MM-DD HH:mm:ss')
    # 计算开始时间和结束时间的小时差，方便计算流量均值
    time_diff = generate_time_diff_hour(ST,ET)
    if input['dstProvince'] !='全国' and input['srcProvince'] !='全国':
        # 生成路由省份的筛选条件
        routeProvienceCon = generate_provience(input['routerProvince'])
        # 生成源端省份的筛选条件
        srcProvinceCon = generate_provience(input['srcProvince'])
        # 生成筛选接口属性条件
        InterfaceTypeCon = generate_interface(input)
        if routeProvienceCon == '':
            routeProvienceCon = srcProvinceCon

        # 目标城市的筛选条件，没有指定则是空
        dstProvinceCon = generate_provience(input['dstProvince'])
        if dstProvinceCon != '' and input['dstProvince'] != '全国':
            dstProvinceCon = f'and dstProvinceCode in {dstProvinceCon}'
        elif dstProvinceCon != '' and input['dstProvince'] == '全国':
            dstProvinceCon = f'and dstProvinceCode not in {dstProvinceCon}'

        # 生成源端类型的条件，没有指定则是空
        srcTypeCon = generate_type(input['srcType'])
        if srcTypeCon != '':
            srcTypeCon = f'and srcType in {srcTypeCon}'

        # 生成目标类型的条件，没有指定则是空
        dstTypeCon = generate_type(input['dstType'])
        if dstTypeCon != '':
            dstTypeCon = f'and dstType in {dstTypeCon}'
        sql = f'''
            select 
                srcProvinceCode,
                dstProvinceCode,
                round(sum(bytes)*8/1000/1000/1000/3600/{time_diff},2) as rate 
            from 
                ngfa_up_analysis.man_idc_analysis_pt1h 
            where 
                timestamp >= '{ST}' and timestamp < '{ET}' 
                and routeProvinceCode in {routeProvienceCon} 
                and srcProvinceCode in {srcProvinceCon} 
                and {InterfaceTypeCon}
                {dstProvinceCon} 
                {srcTypeCon} 
                {dstTypeCon}
            group by srcProvinceCode,dstProvinceCode
        '''
    elif input['dstProvince'] =='全国' or input['srcProvince'] =='全国':
        # 目标城市的筛选条件，没有指定则是空
        dstProvinceCon = generate_provience(input['dstProvince'])
        # 生成源端省份的筛选条件
        srcProvinceCon = generate_provience(input['srcProvince'])
        # 路由省份需与另外一个省份相同，即需要一个统计的角度
        if input['dstProvince'] =='全国':
            SameProvince = srcProvinceCon
            print(dstProvinceCon,srcProvinceCon)
            dstProvinceCon += srcProvinceCon
            routeProvienceCon = srcProvinceCon
            InterfaceTypeCon = "outInterfaceType = 'ut'"
            srcProvinceCon = f'srcProvinceCode in {srcProvinceCon}'
            dstProvinceCon = f'dstProvinceCode not in {dstProvinceCon}'
        else:
            SameProvince = dstProvinceCon
            print(dstProvinceCon, srcProvinceCon)
            srcProvinceCon += dstProvinceCon
            routeProvienceCon = dstProvinceCon
            srcProvinceCon = f'srcProvinceCode not in {srcProvinceCon}'
            dstProvinceCon = f'dstProvinceCode in {dstProvinceCon}'
            InterfaceTypeCon = "inInterfaceType = 'ut'"

        srcTypeCon = generate_type(input['srcType'])
        if srcTypeCon != '':
            srcTypeCon = f'and srcType in {srcTypeCon}'

        # 生成目标类型的条件，没有指定则是空
        dstTypeCon = generate_type(input['dstType'])
        if dstTypeCon != '':
            dstTypeCon = f'and dstType in {dstTypeCon}'
        sql = f"""
            select 
                srcProvinceCode,
                dstProvinceCode,
                round(sum(bytes)*8/1000/1000/1000/3600/{time_diff},2) as rate 
            from 
                ngfa_up_analysis.man_idc_analysis_pt1h 
            where 
                timestamp >= '{ST}' and timestamp < '{ET}' 
                and routeProvinceCode in {routeProvienceCon} 
                and {srcProvinceCon} 
                and {InterfaceTypeCon}
                and {dstProvinceCon} 
                {srcTypeCon} 
                {dstTypeCon}
            group by srcProvinceCode,dstProvinceCode
            union
            select 
                srcProvinceCode,
                dstProvinceCode,
                round(sum(bytes)*8/1000/1000/1000/3600/{time_diff},2) as rate 
            from 
                ngfa_up_analysis.man_idc_analysis_pt1h 
            where 
                timestamp >= '{ST}' and timestamp < '{ET}' 
                and routeProvinceCode in {SameProvince} 
                and srcProvinceCode in {SameProvince} 
                and dstProvinceCode in {SameProvince} 
                and inInterfaceType = 'dt'
                {srcTypeCon} 
                {dstTypeCon}
            group by srcProvinceCode,dstProvinceCode
        """
    else:
        sql = ''
    return sql


if __name__ == '__main__':
    #test1 = {'srcProvince': "'安徽'", 'dstProvince': "'江苏'", 'srcType': "'城域网+IDC'", 'dstType': "'城域网+IDC'", 'routerProvince': "'安徽'", 'startTime': "'2023-12-18 00:00:00'", 'endTime': "'2023-12-18 12:00:00'"}
    #test =
    #test2 = ''
    et = '2023-12-18'
    st = '2023-12-18 00:00:00'
    et = et.format('YYYY-MM—DD HH:mm:ss')
    print(et)
    # a = generate_provience(test)
    #a = generate_interface(test1)
    # a = generate_type(test2)
    #a = generate_time_diff_hour(st,et)
    #print(a)