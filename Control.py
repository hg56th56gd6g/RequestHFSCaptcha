#-*- coding:utf-8 -*-
import asyncio,Sender,logging
from traceback import print_exc
from logging import debug
#是否正在运行,计数器和日志文件
running=True
ok=0
log=open("error.log","a",65536)
#一直发送请求,直到running为False时退出,计数
async def SendLoop(Send):
    global ok,running
    try:
        while running:
            ok+=await Send()
    except Exception as a:
        debug(f"SendLoop error:{a}")
        print_exc(file=log)
#回车退出程序
def WaitForExit():
    input("[小心误触]输入回车退出")
    #关闭SendLoop
    global running
    running=False
#
async def Main():
    print("初始化中...")
    #默认同时运行16个,12个代理4个不代理,超时10秒,不debug
    count=16
    proxy=12
    timeout=10
    #解析命令行python Main.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> [<是否debug>]
    from sys import argv
    count=int(argv[1])
    proxy=int(argv[2])
    timeout=float(argv[3])
    #debug
    if 5<=len(argv) and argv[4]=="True":
        logging.basicConfig(level=logging.DEBUG)
    #检查参数
    if not (1<=count and 0<=timeout and 0<=proxy<=count):
        print("参数错误")
    #学生家长对半分
    roleType=count//2
    #创建count个SendLoop,等待它们全部退出
    connects=[]
    tasks=[]
    for argv in range(count):
        #如果还剩家长类型
        if roleType:
            roleType-=1
            #如果还剩要使用代理
            if proxy:
                proxy-=1
                #家长类型,使用代理
                connects.append(Sender.Sender(
                    timeout,
                    Sender.ROLETYPE_PARENT,
                    True
                ))
                debug("start SendLoop with proxy,roleType=PARENT")
            else:
                #家长类型,不使用代理
                connects.append(Sender.Sender(
                    timeout,
                    Sender.ROLETYPE_PARENT,
                    False
                ))
                debug("start SendLoop,roleType=PARENT")
        else:
            #如果还剩要使用代理
            if proxy:
                proxy-=1
                #学生类型,使用代理
                connects.append(Sender.Sender(
                    timeout,
                    Sender.ROLETYPE_STUDENT,
                    True
                ))
                debug("start SendLoop with proxy,roleType=STUDENT")
            else:
                #学生类型,不使用代理
                connects.append(Sender.Sender(
                    timeout,
                    Sender.ROLETYPE_STUDENT,
                    False
                ))
                debug("start SendLoop,roleType=STUDENT")
        #对每个连接创建SendLoop
        tasks.append(SendLoop(connects[argv].Send))
    #把等待退出的任务也加入
    tasks.append(asyncio.to_thread(WaitForExit))
    #清理一下变量
    del argv,count,timeout,proxy,roleType
    #等待...
    await asyncio.gather(*tasks)
    #结束
    global ok
    ok=f"count={ok}"
    print(ok)
    print(ok,file=log)
    log.close()
asyncio.run(Main())