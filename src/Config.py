#-*- coding:utf-8 -*-
from httpx import Limits, AsyncClient
from random import choice, randint
Timeout = 5

#用户类型
ROLETYPE_STUDENT = 1    #学生
ROLETYPE_PARENT = 2     #家长

#app版本
VersionName = {
    ROLETYPE_STUDENT: "4.31.30",
    ROLETYPE_PARENT: "3.32.35"
}


#创建一个AsyncClient
def CreateAsyncClient(roleType, proxy):
    return AsyncClient(
        base_url = UrlOfBase,
        timeout = Timeout,
        proxies = proxy,
        http1 = True,
        http2 = False,
        verify = False,
        headers = (
            ("deviceType", "1"),
            ("appType", str(roleType)),
            ("versionName", VersionName[roleType]),
            ("User-Agent", "YX Android 12"),
            ("Host", Host)
        ),
        limits = Limits(
            max_keepalive_connections = None,
            max_connections = None,
            keepalive_expiry = None
        ),
        trust_env = True
    )


#请求地址
Host = "hfs-be.yunxiao.com"
UrlOfBase = "https://" + Host
#刷新svg验证码
UrlOfSvg = "/v2/users/captcha"
#手机验证码_注册(需要未注册)
UrlOfRegister = "/v2/native-users/verification-msg-with-captcha"
#手机验证码_找回密码(需要已注册)
UrlOfForgotPWD = "/v2/users/retrieving-msg-code-with-captcha"

#请求头
HeadersOfSvg = ()
HeadersOfCaptcha = (
    ("Content-Type", "application/json; charset=UTF-8"),
)


#随机生成手机号,一个11字节字符串,前三位是号码头,但第一位目前只有'1',后8位是随机数
def CreatePhone():
    return f"1{choice(PhoneHeader)}{str(randint(0,99999999)).zfill(8)}"

#手机号第二位和对应第三位可能的值
PhoneHeader = (
    "30","31","32","33","35","36","37","38","39",
    "50","51","52","53","55","56","57","58","59",
    "62","65","66","67",
    "70","71","72","73","75","76","77","78",
    "80","81","82","83","84","85","86","87","88","89",
    "90","91","92","93","95","96","97","98","99"
)