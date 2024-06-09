#-*- coding:utf-8 -*-
import asyncio, logging, Sender, Config
log = logging.getLogger("RequestHFSCaptcha")
#连接列表
connects = []
#任务列表
tasks = []
#运行状态
running = None
def IsRunning():
    return bool(running.value)


async def AsyncMain():
    await asyncio.gather(*tasks)


def Main(count, proxy, timeout, status):
    global running
    running = status
    roleType = Config.ROLETYPE_PARENT
    use_proxy = False
    Config.Timeout = timeout
    for p in range(count):
        #学生和家长类型对半分
        roleType = (
            Config.ROLETYPE_STUDENT
            if roleType == Config.ROLETYPE_PARENT
            else Config.ROLETYPE_PARENT
        )
        #是否使用代理
        use_proxy = proxy > 0
        proxy -= 1
        #创建任务
        p = Sender.Sender(roleType, use_proxy, p)
        connects.append(p)
        tasks.append(p.SendLoop())
    #运行
    try:
        asyncio.run(AsyncMain())
    except KeyboardInterrupt:
        pass
    return sum(p.count for p in connects)