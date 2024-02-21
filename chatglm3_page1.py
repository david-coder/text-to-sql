#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/30 4:27 PM
# @Author  : baluobo
# @File    : chatglm3_page1.py
# @Description :
import streamlit as st
from chatglm3 import function_chat,draw_bar,prompt_check
#import gradio as gr
from prompt_check import session
#from openai_api_request import function_chat,chat
import json
#from func_tool import draw_pic,draw_pie,draw_line
import streamlit_echarts
#from pyecharts import options as opts
from pyecharts.globals import ThemeType
from clickhouse_driver import Client

st.set_page_config(
    page_title="ChatApp",
    page_icon=" ",
    layout="wide",
)

model = st.sidebar.selectbox('模型选择', ('TrendyLLM based on LLM',),key="model")
user = st.sidebar.selectbox('角色选择', ('ngfa产品数据分析师',),key="user")
st.title('TrendyLLM Analysis Demo For NGFA')

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []


if "chat_message" not in st.session_state:
    st.session_state.chat_message = [{"role": "system", "content": session}]

if "function_message" not in st.session_state:
    st.session_state.function_message = []

# 显示历史信息
for message in st.session_state.history:
    with st.chat_message(
            message["role"]):
        a = str(type(message["content"]))
        if 'pyecharts' in a:
            streamlit_echarts.st_pyecharts(
                message["content"],
                height="500px",
                theme=ThemeType.LIGHT,
            )
        elif 'pandas' in a:
            #st.checkbox("Use container width", value=False, key="use_container_width")
            st.dataframe(message["content"]) #,use_container_width=st.session_state.use_container_width
        else:
            st.write(message["content"])

# user_input接收用户的输入
if user_input := st.chat_input("请输入: "):
    # 在页面上显示用户的输入
    user_message = {"role": "user", "content": f'{user_input}'}
    # 将用户的输入加入历史
    st.session_state.history.append(user_message)
    st.session_state.chat_message.append(user_message)
    print(f'chat_message:{st.session_state.chat_message}')
    with st.chat_message("user"):
        st.markdown(user_input)
        result = prompt_check(st.session_state.chat_message)
        sql, data = function_chat(st.session_state.chat_message)

    # 在页面上显示模型生成的回复
    with st.chat_message("assistant"):
        if sql is False:
            st.markdown(result)
            st.session_state.history.append({"role": "assistant", "content": result})
        else:
            st.markdown(sql)
            st.write(data)
            # 将模型的输出加入到历史信息中
            st.session_state.history.append({"role": "assistant", "content": sql})
            st.session_state.history.append({"role": "assistant", "content": data})

            if data.empty:
                pass
            else:
                bar = draw_bar(data)
                streamlit_echarts.st_pyecharts(
                    bar,
                    height="500px",
                    theme=ThemeType.LIGHT,
                )
                st.session_state.history.append({"role": "assistant", "content": bar})
    #st.session_state.chat_message = [] #{"role": "system", "content": session}
    # 只保留十轮对话，这个可根据自己的情况设定，我这里主要是会把history给大模型，context有限，轮数不能太多
    if len(st.session_state.chat_message) >= 8:
        temp = st.session_state.chat_message[-6:]
        st.session_state.chat_message = [{"role": "system", "content": session}]
        st.session_state.chat_message = st.session_state.chat_message + temp

    if len(st.session_state.history) > 20:
        st.session_state.messages = st.session_state.messages[-20:]
