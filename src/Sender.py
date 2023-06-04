#-*- coding:utf-8 -*-
from GetSvgCaptcha import GetSvgCaptcha
from GetRandomPhone import GetRandomPhone
from GetRandomProxy import GetRandomProxy
from httpx import AsyncClient,Limits
import logging,asyncio
debug=logging.getLogger("RequestHFSCaptcha").debug
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
#失败多少次后将重新连接
MAX_FAIL=3
#当captcha返回4049(等待60s)时等待,而不是视作错误
SENDER_4049_WAIT=True
#一些已知的roleType(这个用来区分帐号类型,但对于本程序用处不大),好分数更新了,必须是下列值之一,否则"参数错误roleType[TYPE]","参数错误roleType[ENUM]"...
ROLETYPE_STUDENT=1        #学生
ROLETYPE_PARENT=2         #家长
#一个Sender对象只有一个连接,可以一直请求手机验证码(内部实现为直到连接不可用,随后新建一个连接),count属性代表这个Sender成功请求了多少次
class Sender:
    def __init__(self,timeout,roleType,proxy):
        self.timeout=timeout
        self.roleType=roleType
        self.proxy=proxy
        #失败计数和成功计数
        self.fail=0
        self.count=0
    #一次match的过程,异步
    async def Match(self,phone=None):
        #有没有自定义手机号
        if phone:
            self.phone=phone
        else:
            #没有就随机获取一个手机号
            self.phone=GetRandomPhone()
        debug(f"Sender: match,roleType={self.roleType},phone={self.phone}")
        #发送请求
        self.response=(await self.connect.get(
            UrlOfMatch,
            headers=HeadersOfMatch,
            params={
                "roleType":self.roleType,
                "account":self.phone
            }
        )).json()
    #多次match直到成功,异步
    async def MatchUntilSuccess(self,phone=None):
        while True:
            if MAX_FAIL<=self.fail:
                return
            await self.Match(phone)
            code=self.response["code"]
            #状态码不是0(成功值)
            if code!=0:
                #其他状态码
                #1001:参数错误
                self.fail+=1
                debug(f"Sender: match error with {code}")
                continue
            #手机号已被注册
            if self.response["data"]["occupied"]:
                debug("Sender: phone is exists")
                continue
            break
    #一次不需要svg的captcha过程,异步
    async def Captcha(self):
        debug(f"Sender: captcha,roleType={self.roleType},phone={self.phone}")
        self.response=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType
            }
        )).json()
    #一次需要svg的captcha过程,异步
    async def CaptchaWithSvg(self):
        code=GetSvgCaptcha(self.response["data"]["pic"])
        debug(f"Sender: captcha with svg,roleType={self.roleType},phone={self.phone},svg={code}")
        self.response=(await self.connect.post(
            UrlOfCaptcha,
            headers=HeadersOfCaptcha,
            json={
                "phoneNumber":self.phone,
                "roleType":self.roleType,
                "code":code
            }
        )).json()
    #这个函数实现了完整请求手机验证码的过程(可以输入自定义的phone),并一直请求直到连接并不可用,异步
    async def Send(self,phone=None):
        #创建新连接,并保证连接关闭
        debug(f"Sender: create a new connect,timeout={self.timeout},roleType={self.roleType},proxy={self.proxy}")
        async with AsyncClient(
            timeout=self.timeout,
            limits=Limits,
            http2=True,
            proxies=(await GetRandomProxy()) if self.proxy else None,
            base_url=UrlOfBase,
            headers=HeadersOfBase,
            trust_env=False
        ) as self.connect:
            #充分利用每一个连接,有一个失败计数,当超过阈值则重新连接
            while True:
                self.fail=0
                await self.MatchUntilSuccess(phone)
                #使用captcha还是captcha with svg
                NowCaptcha=self.Captcha
                #充分利用每一个match
                while True:
                    if MAX_FAIL<=self.fail:
                        return
                    await NowCaptcha()
                    code=self.response["code"]
                    #code:0,成功
                    if code==0:
                        debug("Sender: captcha success!!!")
                        self.count+=1
                        #继续申请captcha
                        NowCaptcha=self.Captcha
                        continue
                    #code:4048,需要图形验证码
                    elif code==4048:
                        debug("Sender: captcha need svg...")
                        #captcha with svg跟不需要svg的captcha请求共用一个解析
                        NowCaptcha=self.CaptchaWithSvg
                        continue
                    #code:4049,60s后才能重新发送(并且设置了等待的flag)
                    elif code==4049 and SENDER_4049_WAIT:
                        debug("Sender: wait 60s...")
                        await asyncio.sleep(60)
                        NowCaptcha=self.Captcha
                        continue
                    #其他状态码,要重新match或重连
                    #code:1001,参数错误,以下情况也会:没match就请求的时候,与match的请求不是同一个连接,与match的请求不是同一个手机号
                    #code:4047,超出限制,不知道具体啥意思
                    else:
                        self.fail+=1
                        NowCaptcha=self.Captcha
                        debug(f"Sender: captcha error with {code}")
                        await self.MatchUntilSuccess(phone)
                        continue