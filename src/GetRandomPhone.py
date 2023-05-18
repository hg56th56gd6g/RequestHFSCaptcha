#-*- coding:utf-8 -*-
from random import choice,randint
#储存了第二位和对应第三位可能的值
PhoneHeader=(
    "30","31","32","33","35","36","37","38","39",
    "50","51","52","53","55","56","57","58","59",
    "62","65","66","67",
    "70","71","72","73","75","76","77","78",
    "80","81","82","83","84","85","86","87","88","89",
    "90","91","92","93","95","96","97","98","99"
)
#随机获取一个手机号,一个11字节字符串,第一位一定是'1',fstring比printf风格的格式化和format快一些
def GetRandomPhone():
    return f"1{choice(PhoneHeader)}{str(randint(0,99999999)).zfill(8)}"