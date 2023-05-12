#-*- coding:utf-8 -*-
from GetSvgCaptcha import GetSvgCaptcha
from GetRandomPhone import GetRandomPhone
from GetRandomProxy import GetRandomProxy
from httpx import AsyncClient,Limits
from logging import debug
#要用的一些请求数据,配置文件
UrlOfBase="https://hfs-be.yunxiao.com"
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
#没有连接限制
Limits=Limits(max_keepalive_connections=None,max_connections=None,keepalive_expiry=None)
#一些已知的roleType(这个用来区分帐号类型,但对于本程序用处不大),好分数更新了,必须是下列值之一,否则"参数错误roleType[TYPE]","参数错误roleType[ENUM]"...
ROLETYPE_STUDENT=1        #学生
ROLETYPE_PARENT=2         #家长
#一个Sender对象只有一个连接,可以一直请求手机验证码(内部实现为直到连接不可用,随后新建一个连接)
class Sender:
    def __init__(self,timeout,roleType,proxy):
        self.timeout=timeout
        self.roleType=roleType
        self.proxy=proxy
        #创建连接
        self.Connect()
    #创建新的连接
    def Connect(self):
        #创建新连接
        self.connect=AsyncClient(
            timeout=self.timeout,
            limits=Limits,
            http2=True,
            proxies=GetRandomProxy() if self.proxy else None,
            base_url=UrlOfBase,
            headers=HeadersOfBase
        )
    #一次match的过程,异步
    async def Match(self,phone=None):
        #有没有自定义手机号
        if phone:
            self.phone=phone
        else:
            #没有就随机获取一个手机号
            self.phone=GetRandomPhone()
        #发送请求
        self.respones=(await self.connect.get(
            UrlOfMatch,
            headers=HeadersOfMatch,
            params={
                "roleType":self.roleType,
                "account":self.phone
            }
        )).json()
    #一次不需要svg的captcha过程,异步
    async def Captcha(self):
        self.respones=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType
            }
        )).json()
    #一次需要svg的captcha过程,异步
    async def CaptchaWithSvg(self):
        self.respones=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType,
                "code":GetSvgCaptcha(self.respones["data"]["pic"])
            }
        )).json()
    #这个函数实现了完整请求手机验证码的过程(可以输入自定义的phone),返回成功请求的次数,异步
    async def Send(self,phone=None):
        count=0
        #match
        await self.Match(phone)
        #状态码不是0(成功值),或者手机号已被注册
        if self.respones["code"] or self.respones["data"]["occupied"]:
            #其他状态码
            #1001:参数错误
            debug("Sender: match error")
            return count
        #captcha
        await self.Captcha()
        #captcha的状态码,只要不需要重新match就一直请求,充分利用一个match
        while True:
            #code:0,成功,继续申请captcha
            if self.respones["code"]==0:
                debug("Sender: captcha success!!!")
                count+=1
                #继续申请captcha
                await self.Captcha()
                continue
            #code:4048,需要图形验证码,不返回
            elif self.respones["code"]==4048:
                debug("Sender: captcha need svg...")
                #captcha with svg
                await self.CaptchaWithSvg()
                #这里跟不需要svg的captcha请求共用一个解析
                continue
            #其他状态码,统一重新连接,然后返回
            #code:1001,参数错误,出现在没match就请求的时候,与match的请求不是同一个连接,与match的请求不是同一个手机号,或者就是字面意思比如长度不对等
            #code:4047,超出限制,不知道具体啥意思
            #code:4049,60s后才能重新发送
            debug("Sender: captcha return a unknown code,reconnect...")
            await self.connect.aclose()
            self.Connect()
            return count