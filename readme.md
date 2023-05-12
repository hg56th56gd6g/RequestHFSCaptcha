#运行要求

python3.7+(推荐3.10以上,这是我的运行环境)

`pip install httpx[brotli,http2,socks]`

一个https://github.com/jhao104/proxy_pool的代理池,获取随机代理在http://127.0.0.1:5010/get

或者你也可以在"GetRandomProxy.py"里将UrlOfProxy改为你自己的获取随机代理api

在win64的二进制文件里有提供它的运行环境,第一次运行前你需要进入"RequestHFSCaptcha\ProxyPool"输入命令`pip install -r requirements.txt`

之后你只需要输入`python main.py`即可运行代理池,这会新建一个cmd窗口,是redis的,当前窗口被用于运行代理池服务器,这些子进程全部打开后main.py会退出,不用担心有一个空闲进程的问题 :)

# 使用方式

python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> \[<是否debug>\]

注意:绝大多数情况下不要打开debug,如果确实要使用debug,请在后面添加"True"参数

推荐配置: `python Control.py 16 12 10`

双击"Default.bat"可以启动代理池,然后运行默认配置,不过这些都需要您手动关闭

就是这样!

#更新日志

相比于之前的库,使用asyncio全面重构,并且提供了更适合人类阅读的api

玩的开心 :D