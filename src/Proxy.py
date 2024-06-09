#-*- coding:utf-8 -*-
from httpx import AsyncClient, HTTPError
import logging, asyncio, Control
log = logging.getLogger("RequestHFSCaptcha")
AsyncClient = AsyncClient(
    base_url = "http://127.0.0.1:5010/",
    trust_env = False
)


#获取剩余代理数量
async def GetCount():
    return (await AsyncClient.get("count/")).json()["count"]


#随机获取代理
async def GetRandomProxy():
    while Control.IsRunning():
        try:
            #从https://github.com/jhao104/proxy_pool的代理池获取
            r = (await AsyncClient.get("get/")).json().get("proxy")
            if r:
                return "http://" + r
            raise HTTPError("no available proxy")
        except HTTPError as a:
            #没获取到
            log.debug(f"[ProxyPool]get random proxy error({a}), retry after 5s...")
            await asyncio.sleep(5)