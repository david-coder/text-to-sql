#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/27 3:16 PM
# @Author  : baluobo
# @File    : func_tool.py
# @Description :

from pyecharts import options as opts
from pyecharts.charts import Bar,Pie,Line
from pyecharts.faker import Faker
import decimal

functions_draw_bar = [{
        "name": "draw_pic",
        "description": f"该方法用于生成柱状图"
                       f"例1数据为：'srcProvinceCode': ['JS','JS','JS','JS'], 'dstProvinceCode': ['JS','BJ','ZJ','AH'],'flow':[1000,2340,342,34121]"
                       f"则xAxis为['JS','BJ','ZJ','AH']，yAxis为[1000,2340,342,34121]，y_name为'JS'",
        "parameters": {
            "type": "object",
            "properties": {
                "xAxis": {
                    "type": "array",
                    "items":{
                        "type": "String"
                    },
                    "description": "柱状图的横坐标"
                },
                "yAxis":{
                    "type": "array",
                    "items":{
                        "type": "number"
                    },
                    "description": "柱状图的纵坐标"
                },
                "x_name":{
                    "type":"string",
                    "description":"柱状图的横坐标的标题"
                },
                "y_name":{
                    "type":"string",
                    "description":"柱状图的纵坐标的标题"
                }
            },
            "required": ["xAxis", "yAxis","x_name","y_name"],
        }
    }]

def draw_pic(xAxis, yAxis, xAxis_name, yAxis_name):
    print(xAxis, yAxis, xAxis_name, yAxis_name)
    yAxis = [round(i,1) for i in yAxis]
    b = (
        Bar()
        .add_xaxis(xAxis)
        .add_yaxis(yAxis_name, yAxis)
        .set_global_opts(xaxis_opts=opts.AxisOpts(name=xAxis_name, axislabel_opts={"rotate": 70}),
                         datazoom_opts=opts.DataZoomOpts(orient='horizontal'))

        #.render("bar_base.html")
    )
    return b

def draw_pie(attr_name,value):
    value = [round(i, 1) for i in value]
    p = (Pie()
         .add("", [list(z) for z in zip(attr_name,value)])
         .set_global_opts(
            title_opts=opts.TitleOpts(title="Pie-Radius"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"))
         .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
         #.render("pie_radius.html")
    )
    return p

def draw_line(xAxis, xAxis_name,yAxis,yAxis_name,yAxis_cat):
    print()
    yAxis = [round(float(i), 1) for i in yAxis]
    l = (Line()
         .add_xaxis(xAxis)
         .add_xaxis(yAxis_cat,yAxis,is_select = False,label_opts=opts.LabelOpts(is_show=False))
    )
    # for attr,v in zip(yAxis,yAxis_name):
    #     l.add_xaxis(attr,[round(i,1) for i in v],is_select = False,label_opts=opts.LabelOpts(is_show=False))
    return l