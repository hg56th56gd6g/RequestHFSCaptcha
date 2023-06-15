#-*- coding:utf-8 -*-
from GetSvgCaptcha import GetSvgCaptcha
from Phone import GetRandomPhone
from Proxy import GetRandomProxy
from httpx import AsyncClient,Limits
import logging,asyncio
logging=logging.getLogger("RequestHFSCaptcha")
info=logging.info
debug=logging.debug
#设置停止
running=True
#要用的一些请求数据,配置文件
UrlOfBase="://hfs-be.yunxiao.com"
UrlOfMatch="/v2/users/matched-users"
UrlOfCaptcha="/v2/native-users/verification-msg-with-captcha"
HeadersOfBase={
    "accept":"application/json",
    "origin":"https://www.haofenshu.com",
    "referer":"https://www.haofenshu.com/",
    "sec-ch-ua":"\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform":"\"Windows\"",
    "sec-fetch-dest":"empty",
    "sec-fetch-mode":"cors",
    "sec-fetch-site":"cross-site",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}
HeadersOfMatch={
}
HeadersOfCaptcha={
    "content-type":"application/json;charset=UTF-8"
}
#最多失败次数限制(发生http错误则无视限制直接失败)
MAX_FAIL=4
#最多重试次数
MAX_RETRY=32
#没有连接限制
Limits=Limits(max_keepalive_connections=None,max_connections=None,keepalive_expiry=None)
#一些已知的roleType(这个用来区分帐号类型,但对于本程序用处不大),好分数更新了,必须是下列值之一,否则"参数错误roleType[TYPE]","参数错误roleType[ENUM]"...
ROLETYPE_STUDENT=1        #学生
ROLETYPE_PARENT=2         #家长

#一个Sender对象只有一个连接,可以一直请求手机验证码(内部实现为直到连接不可用,随后新建一个连接),count属性代表这个Sender成功请求了多少次
class Sender:
    def __init__(self,timeout,roleType,proxy):
        self.timeout=timeout
        self.roleType=roleType
        self.proxy=True if proxy else None
        #成功计数
        self.count=0
        #失败计数
        self.fail=0
        #重试计数
        self.retry=0
        #当前客户端方是否支持https
        self.https=True
        #当前连接
        self.connect=None
        #当前手机号
        self.phone=None
        #当前的response对象
        self.response=None
        #当前的请求数据
        self.data=None
        #当前的svg验证码
        self.code=None
        #当前使用的captcha函数
        self.NowCaptcha=None
    #随机等待一段时间模拟人类操作
    @staticmethod
    async def ImAHuman():
        await asyncio.sleep(1)
    #一次match的过程,异步,成功返回True,失败返回False
    async def Match(self,phone=None):
        #有没有自定义手机号
        if phone:
            self.phone=phone
        else:
            #没有就随机获取一个手机号
            self.phone=GetRandomPhone()
        debug(f"[Sender]match,roleType={self.roleType},phone={self.phone}")
        #发送请求
        self.response=(await self.connect.get(
            UrlOfMatch,
            headers=HeadersOfMatch,
            params={
                "roleType":self.roleType,
                "account":self.phone
            }
        ))
        self.data=self.response.json()
        #解析请求
        await self.ImAHuman()
        code=self.data.get("code")
        #状态码不是0(成功值)
        if code!=0:
            #其他状态码
            #1001:参数错误
            self.fail+=1
            debug(f"[Sender]match error:{code}:{self.data.get('msg')}")
            return False
        #手机号已被注册
        if self.data["data"]["occupied"]:
            debug("[Sender]phone is exists")
            return False
        return True
    #一次不需要svg的captcha过程,异步
    async def Captcha(self):
        debug(f"[Sender]captcha,roleType={self.roleType},phone={self.phone}")
        self.response=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType
            }
        ))
    #一次需要svg的captcha过程,异步
    async def CaptchaWithSvg(self):
        if not self.code:
            #可以指定code,没有则自动识别
            self.code=GetSvgCaptcha(self.data["data"]["pic"])
        debug(f"[Sender]captcha with svg,roleType={self.roleType},phone={self.phone},svg={self.code}")
        self.response=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType,
                "code":self.code
            }
        ))
    #解析Captcha/CaptchaWithSvg,异步,返回True代表重新match,报错了代表连接不可用
    async def ParseCaptcha(self):
        await self.ImAHuman()
        #如果收到了451状态码,则再次尝试(不改变上次状态)
        if self.response.status_code==451:
            #到达最大重试次数,视为错误
            if MAX_RETRY<=self.retry:
                self.fail+=1
                debug("[Sender]captcha error:too many retry")
                return True
            self.retry+=1
            debug("[Sender]captcha has http(451),retry...")
            return
        self.retry=0
        #开始解析
        self.data=self.response.json()
        code=self.data["code"]
        #code:0,成功
        if code==0:
            debug("[Sender]captcha success!!!")
            self.count+=1
            #继续请求验证码
            self.NowCaptcha=self.Captcha
        #code:4048,需要图形验证码
        elif code==4048:
            #删除当前的svg验证码
            self.code=None
            debug("[Sender]captcha need svg...")
            self.NowCaptcha=self.CaptchaWithSvg
        #code:4049,60s后才能重新发送,申请普通captcha
        elif code==4049:
            debug("[Sender]captcha need wait 60s...")
            self.NowCaptcha=self.Captcha
            #这个等待一分钟的任务在结束时要被取消
            code=asyncio.create_task(asyncio.sleep(60))
            code.set_name("CancelThisSleep")
            await code
        #其他状态码,要重新match或重连
        #code:1001,参数错误,以下情况也会:没match就请求的时候,与match的请求不是同一个连接,与match的请求不是同一个手机号
        #code:4047,当天短信次数超限,请明天再试
        else:
            self.fail+=1
            debug(f"[Sender]captcha error:{code}:{self.data.get('msg')}")
            return True
    #创建一个连接的配置
    def Connect(self):
        debug(f"[Sender]create a new connect,timeout={self.timeout},roleType={self.roleType},proxy={self.proxy}")
        self.connect=AsyncClient(
            timeout=self.timeout,
            limits=Limits,
            http1=True,
            http2=True,
            proxies=self.proxy,
            base_url=("https" if self.https else "http")+UrlOfBase,
            headers=HeadersOfBase,
            trust_env=False
        )
    #这个函数实现了一次完整请求手机验证码的过程(可以输入自定义的phone),异步
    async def Send(self,phone=None):
        #创建新连接
        if running==False:
            return
        if self.proxy:
            self.proxy="http://"+(await GetRandomProxy())
        self.Connect()
        async with self.connect:
            #充分利用每一个连接
            while True:
                self.fail=0
                #这里是重新match,直到成功
                while True:
                    if running==False or MAX_FAIL<=self.fail:
                        return
                    #match成功
                    if (await self.Match(phone)):
                        break
                #第一次一定是普通captcha
                self.NowCaptcha=self.Captcha
                #充分利用每一个match
                while True:
                    if running==False or MAX_FAIL<=self.fail:
                        return
                    await self.NowCaptcha()
                    #重新match
                    if (await self.ParseCaptcha()):
                        break