#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/26 2:20 PM
# @Author  : baluobo
# @File    : generate_ngfa_sql.py
# @Description :

import json
from datetime import datetime

type_dict = {'IDC':'1','城域网':'2','IDC客户':'3','中国移动':'4','中国联通':'5','DNS':'6','ITV':'7','NOC':'8',
             'PT':'9','QXZX':'10','SOC':'11','SW':'12','WG':'13','WLW':'14','DX-YD':'15'}

provience_dict = {'海南': 'HI', '江苏': 'JS', '宁夏': 'NX', '安徽': 'AH', '重庆': 'CQ', '甘肃': 'GS', '黑龙江': 'HL', '吉林': 'JL',
                  '辽宁': 'LN', '贵州': 'GZ', '新疆': 'XJ', '西藏': 'XZ', '云南': 'YN', '福建': 'FJ', '青海': 'QH', '四川': 'SC',
                  '上海': 'SH', '广西': 'GX', '陕西': 'SN', '北京': 'BJ', '河南': 'HA', '山西': 'SX', '广东': 'GD', '湖北': 'HB',
                  '江西': 'JX', '河北': 'HE', '湖南': 'HN', '内蒙古': 'NM', '山东': 'SD', '天津': 'TJ', '浙江': 'ZJ'}



def prepocess(function_result):
    function_result = function_result.replace("(","").replace(")","")
    #json_result = json.loads(function_result)
    condition = function_result.split(',')
    condition_dict={}
    for con in condition:
        con_list = con.split('=')
        condition_dict[con_list[0].replace(' ','')] = con_list[1].replace("'",'').replace('\n','')
    return condition_dict

def generate_provience(condition):
    condition_tuple = ()
    if "+" in condition:
        condition_list = condition.split("+")
        for con in condition_list:
            con = con.replace("'")
            condition_tuple += provience_dict[con]
        provience_condition = condition_tuple
    else:
        try:
            condition = condition.replace("'",'')
            provience_condition = provience_dict[condition]
        except Exception as e:
            print(e)
            provience_condition = ''
    return provience_condition

def generate_type(condition):
    condition_tuple = ()
    if condition == "":
        type_condition = ''
    elif '+' in condition:
        condition_list = condition.split("+")
        for con in condition_list:
            condition_tuple += (type_dict[con],)
        type_condition = condition_tuple
    else:
        try:
            type_condition = type_dict[condition]
            condition_tuple += (type_condition,)
            type_condition = condition_tuple
        except Exception as e:
            print(e)
            type_condition = ''
    return type_condition

def generate_interface(condition):
    # 源端省份与目标省份相同
    print(condition['srcProvince'],condition['dstProvince'],condition['routerProvince'])
    if condition['srcProvince'] == condition['dstProvince']:
        interface_condition = "inInterfaceType = 'dt'"
    elif condition['routerProvince'] == '' or condition['srcProvince'] == condition['routerProvince']:
        interface_condition = "outInterfaceType = 'ut'"
    elif condition['dstProvince'] == condition['routerProvince']:
        interface_condition = "inInterfaceType = 'ut'"
    else:
        interface_condition = "outInterfaceType = 'ut'"
    return interface_condition

def generate_time_diff_hour(st,et):
    startTime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
    endTime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S")
    hour_diff = (endTime - startTime).total_seconds() / 60 / 60
    #print("两个时间相差{}小时".format(int(hour_diff)))
    return abs(hour_diff)

def generate_settlement_sql(input):
    # 这些是必须要有的
    ST = input['startTime']
    ET = input['endTime']
    time_diff = generate_time_diff_hour(ST,ET)
    routeProvienceCon = generate_provience(input['routerProvince'])
    srcProvinceCon = generate_provience(input['srcProvince'])
    InterfaceTypeCon = generate_interface(input)

    dstProvinceCon = generate_provience(input['dstProvince'])
    if dstProvinceCon != '':
        dstProvinceCon = f'and dstProvinceCode = {dstProvinceCon}'

    srcTypeCon = generate_type(input['srcType'])
    if srcTypeCon != '':
        srcTypeCon = f'and srcType in {srcTypeCon}'
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
            and routeProvinceCode = {routeProvienceCon} 
            and srcProvinceCode = {srcProvinceCon} 
            and {InterfaceTypeCon}
            {dstProvinceCon} 
            {srcTypeCon} 
            {dstTypeCon}
        group by srcProvinceCode,dstProvinceCode
    '''
    return sql


if __name__ == '__main__':
    #test1 = {'srcProvince': "'安徽'", 'dstProvince': "'江苏'", 'srcType': "'城域网+IDC'", 'dstType': "'城域网+IDC'", 'routerProvince': "'安徽'", 'startTime': "'2023-12-18 00:00:00'", 'endTime': "'2023-12-18 12:00:00'"}
    #test =
    #test2 = ''
    et = '2023-12-18 12:00:00'
    st = '2023-12-18 00:00:00'
    # a = generate_provience(test)
    #a = generate_interface(test1)
    # a = generate_type(test2)
    #a = generate_time_diff_hour(st,et)
    print(a)