#-*- coding:utf-8 -*-
import logging, asyncio, Config, Control
from Proxy import GetRandomProxy
from httpx import HTTPError
from ssl import SSLError
from json import JSONDecodeError
from GetSvgCaptcha import SvgError, GetSvgCaptcha
log = logging.getLogger("RequestHFSCaptcha")

#http响应内容与预期不符
class ContentError(Exception):pass


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
        #记录最后一个请求结果用于错误信息
        self.lr = None

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
        self.lr = r = (await self.cl.post(
            self.method,
            headers = Config.HeadersOfCaptcha,
            data = f'{{"code":"{self.code}","phoneNumber":"{self.phone}","roleType":{self.roleType}}}'
        ))
        #如果收到了451状态码,这是被限制ip了,稍后再次尝试(不改变上次状态)
        if r.status_code == 451:
            log.debug(f"{self.sid}captcha has http(451), retry after 4s...")
            return asyncio.sleep(4)
        #非正确响应
        if r.status_code != 200:
            raise ContentError(f"error http code: {r.status_code} {r.reason_phrase}")
        #处理响应
        data = r.json()
        try:
            nk = "code"
            code = data.get(nk)
            if code is None:
                raise ContentError
            nk = "msg"
            msg = data.get(nk)
            if msg is None:
                raise ContentError
            #0: 成功
            if code == 0:
                log.debug(f"{self.sid}captcha success: {msg}")
                self.count += 1
                self.code = ""
            #4011: 该账户不存在
            elif code == 4011:
                log.debug(f"{self.sid}user not exist: {msg}")
                self.method = Config.UrlOfRegister
                self.code = ""
            #4044: 手机号已被注册
            elif code == 4044:
                log.debug(f"{self.sid}user already exist: {msg}")
                self.method = Config.UrlOfForgotPWD
                self.code = ""
            #4048: 需要图形验证码
            elif code == 4048:
                log.debug(f"{self.sid}captcha need svg: {msg}")
                nk = "data"
                data = data.get(nk)
                if data is None:
                    raise ContentError
                nk = "pic"
                data = data.get(nk)
                if data is None:
                    raise ContentError
                self.code = GetSvgCaptcha(data)
            #其他情况: 更换手机号
            #1001: 参数错误
            #4047: (此手机号)当天短信次数超限,请明天再试
            #4049: 60s后才能重新发送
            else:
                log.debug(f"{self.sid}captcha error: {code}: {msg}")
                self.NewPhone()
        except ContentError:
            raise ContentError(f"data not have key: {nk}")
        return asyncio.sleep(1)

    #申请一个新的svg验证码
    async def NewSvg(self):
        log.debug(f"{self.sid}new svg, phone={self.phone}")
        self.lr = r = (await self.cl.get(
            f"{Config.UrlOfSvg}?phone={self.phone}",
            headers = Config.HeadersOfSvg
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
                #随机生成的手机号,未注册的可能性远大于已注册
                self.code = ""
                self.method = Config.UrlOfRegister
                self.NewPhone()
                if self.proxy:
                    self.proxy = await GetRandomProxy()
                self.Connect()
                async with self.cl:
                    while Control.IsRunning():
                        await (await self.CaptchaWithSvg())
            #忽略这些错误
            except (HTTPError, SSLError) as p:
                log.debug(f"{self.sid}exception: {repr(p)}")
            except (ContentError, SvgError, JSONDecodeError) as p:
                log.debug(f"{self.sid}exception: {repr(p)}: {self.lr.text}")