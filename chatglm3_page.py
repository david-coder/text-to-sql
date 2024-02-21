#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/27 2:38 PM
# @Author  : baluobo
# @File    : chatglm3_page.py
# @Description :
import streamlit as st
from chatglm3 import function_chat,draw_bar
#import gradio as gr
import pymysql
import pandas as pd
#from openai_api_request import function_chat,chat
import json
#from func_tool import draw_pic,draw_pie,draw_line
import streamlit_echarts
#from pyecharts import options as opts
from pyecharts.globals import ThemeType
from clickhouse_driver import Client


model = st.sidebar.selectbox('模型选择', ('TrendyLLM based on LLM',),key="model")
user = st.sidebar.selectbox('角色选择', ('ngfa产品数据分析师',),key="user")

def streamlit_demo():
    st.write("")
    a = st.session_state['q']
    model = st.session_state['model']
    user = st.session_state['user']
    print(model,user)
    if a:
        print(a)
        sql,data = function_chat(a)
        print(sql)
        st.write(sql)
        st.write(data)
        if data.empty:
            pass
        else:
            bar = draw_bar(data)
            streamlit_echarts.st_pyecharts(
                bar,
                height="500px",
                theme=ThemeType.LIGHT,
                key=f"bar"
            )

a = st.text_input("Question", key='q')
print(a)
d = st.button("Click")
if d:
    streamlit_demo()






