#-*- coding:utf-8 -*-
import logging, asyncio, Config, Control
from Proxy import GetRandomProxy
from httpx import HTTPError
from ssl import SSLError
from GetSvgCaptcha import SvgError, GetSvgCaptcha
log = logging.getLogger("RequestHFSCaptcha")


class Sender:
    def __init__(self, roleType, proxy, SenderID = ""):
        self.roleType = roleType
        self.proxy = proxy
        self.sid = f"[Sender_{SenderID}]"
        #成功计数
        self.count = 0
        #当前连接
        self.cl = None
        #当前手机号
        self.phone = None
        #验证码识别结果
        self.code = ""

    #等待一段时间模拟人类操作
    async def ImAHuman(self, time = 0):
        await asyncio.sleep(time)

    #更新手机号码
    def NewPhone(self, phone = None):
        self.phone = phone if phone else Config.CreatePhone()

    #创建连接
    def Connect(self):
        log.debug(f"{self.sid}create a new connect, proxy={self.proxy}")
        self.cl = Config.CreateAsyncClient(self.roleType, self.proxy)

    #申请发送验证码
    async def CaptchaWithSvg(self):
        log.debug(f"{self.sid}captcha, roleType={self.roleType}, phone={self.phone}, code={self.code}, method={self.method}")
        r = (await self.cl.post(
            self.method,
            headers = Config.HeadersOfCaptcha,
            data = f'{{"code":"{self.code}","phoneNumber":"{self.phone}","roleType":{self.roleType}}}'
        ))
        #如果收到了451状态码,这是被限制ip了,稍后再次尝试(不改变上次状态)
        if r.status_code == 451:
            log.debug(f"{self.sid}captcha has http(451), retry after 4s...")
            return self.ImAHuman(4)
        #处理响应
        data = r.json()
        code = data["code"]
        msg = data["msg"]
        #0: 成功
        if code == 0:
            log.debug(f"{self.sid}captcha success: {msg}")
            self.count += 1
            self.code = ""
        #4048: 需要图形验证码
        elif code == 4048:
            log.debug(f"{self.sid}captcha need svg: {msg}")
            self.code = GetSvgCaptcha(data["data"]["pic"])
        #其他情况: 更换手机号
        #1001: 参数错误
        #4011: 该账户不存在
        #4044: 手机号已被注册
        #4047: (此手机号)当天短信次数超限,请明天再试
        #4049: 60s后才能重新发送
        else:
            log.debug(f"{self.sid}captcha error: {code}: {msg}")
            self.NewPhone()
        return self.ImAHuman(1)

    #申请一个新的svg验证码
    async def NewSvg(self):
        log.debug(f"{self.sid}new svg, phone={self.phone}")
        r = (await self.cl.get(
            Config.UrlOfSvg,
            headers = Config.HeadersOfSvg,
            params = (
                ("phone", self.phone),
            )
        ))
        data = r.json()
        msg = data["msg"]
        if data["code"]:
            log.debug(f"{self.sid}new svg error: {msg}")
            return ""
        else:
            log.debug(f"{self.sid}new svg success: {msg}")
            return data["data"]["pic"]

    #这个函数实现了一直请求手机验证码的过程
    async def SendLoop(self):
        #创建新连接
        while Control.IsRunning():
            try:
                self.method = Config.GetUrlOfCaptcha()
                self.NewPhone()
                if self.proxy:
                    self.proxy = await GetRandomProxy()
                self.Connect()
                wait = self.ImAHuman()
                async with self.cl:
                    while Control.IsRunning():
                        await wait
                        wait = await self.CaptchaWithSvg()
                asyncio.create_task(wait).cancel()
            #忽略这些错误
            except (HTTPError, SSLError, SvgError) as p:
                log.debug(f"{self.sid}exception: {repr(p)}")