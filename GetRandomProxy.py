#-*- coding:utf-8 -*-
from httpx import Client,Request
import logging
debug=logging.getLogger("RequestHFSCaptcha").debug
#代理库来源:https://github.com/jhao104/proxy_pool
Client=Client()
#更小的请求
Request=Request(
    "GET",
    "http://127.0.0.1:5010/get/",
    headers={
        "connection":"keep-alive"
    }
)
#随机获取代理
def GetRandomProxy(proxy):
    #不使用代理
    if not proxy:
        return None
    #尝试获取代理直到成功
    while True:
        respones=Client.send(Request).json().get("proxy")
        if respones:
            return "http://"+respones
        debug("get random proxy error,retry...")