#!/usr/bin python
#coding: utf8
import requests
import json


def get_turing_response(req=""):
    url = "http://www.tuling123.com/openapi/api"
    secretcode = "嘿嘿，这个就不说啦"
    response = requests.post(url=url, json={"key": secretcode, "info": req, "userid": 12345678})
    return json.loads(response.text)['text'] if response.status_code == 200 else ""

def get_qingyunke_response(req=""):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg={}".format(req)
    response = requests.get(url=url)
    return json.loads(response.text)['content'] if response.status_code == 200 else ""

# 简单做下。后面慢慢来
def get_response_by_keyword(keyword):
    if '排行' in keyword:
        result = {"type": "image","content":"jvSOdrLaYomfxXpJZfgDbNvglFHy7OsJvVlnwkRXLLC7ciEkhzZ9wggOPeaIM0oB"}
    elif '大户' in keyword:
        result = {"type": "image","content":"jvSOdrLaYomfxXpJZfgDbNvglFHy7OsJvVlnwkRXLLC7ciEkhzZ9wggOPeaIM0oB"}
    elif '持仓' in keyword:
        result = {"type": "image","content":"jvSOdrLaYomfxXpJZfgDbNvglFHy7OsJvVlnwkRXLLC7ciEkhzZ9wggOPeaIM0oB"}
    elif '出入金' in keyword:
        result = {"type": "image","content":"45mBSMZtUimRIOsGJOwHqmmDfPvC6_GYHqDYkJ10K79qoAYSvNvXh18rs84NAKox"}
    else:
        result = {"type": "text", "content": "获取账户信息"}
    return result