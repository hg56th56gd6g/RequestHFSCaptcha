#-*- coding:utf-8 -*-
from httpx import AsyncClient,Request,HTTPError
import logging,asyncio
logging=logging.getLogger("RequestHFSCaptcha")
info=logging.info
debug=logging.debug
AsyncClient=AsyncClient(
    base_url="http://127.0.0.1:5010/",
    trust_env=False
)
#获取剩余代理数量
async def GetCount():
    return (await AsyncClient.get("count/")).json()["count"]
#随机获取代理
async def GetRandomProxy():
    #尝试获取代理直到成功
    while True:
        try:
            #从https://github.com/jhao104/proxy_pool的代理池获取
            response=(await AsyncClient.get("get/")).json().get("proxy")
            if response:
                return response
            raise HTTPError("no available proxy")
        except HTTPError as a:
            #没获取到
            debug(f"[ProxyPool]get random proxy error({a}),retry after 10s...")
            await asyncio.sleep(10)