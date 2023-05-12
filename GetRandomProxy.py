#-*- coding:utf-8 -*-
from httpx import Client
#代理库来源:https://github.com/jhao104/proxy_pool
UrlOfProxy="http://127.0.0.1:5010/get/"
#连接复用
Client=Client()
#随机获取代理
def GetRandomProxy():
    while True:
        respones=Client.get(UrlOfProxy).json().get("proxy")
        if respones:
            return "http://"+respones