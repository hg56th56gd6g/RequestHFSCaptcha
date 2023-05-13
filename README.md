![AttackHFS](/icons/icon.png)

# 运行要求

## 1.

python3.8+(推荐3.10以上,这是我的运行环境)

## 2.

在1.的python环境里`pip install httpx[brotli,http2,socks]`

## 3.

一个https://github.com/jhao104/proxy_pool的代理池,获取随机代理在http://127.0.0.1:5010/get/

或者你也可以修改GetRandomProxy.py来使用你自己的获取随机代理

在win64的二进制文件里有提供默认代理池的运行环境,第一次运行前你需要进入"RequestHFSCaptcha\ProxyPool"输入命令`pip install -r requirements.txt`

注:用跟1.一样的python环境就行,或者你愿意新开一个也行

之后的每次运行你只需要输入`python main.py`即可运行代理池,这会新建三个cmd窗口,不要关闭它们

注:加上main.py的有四个窗口,main.py结束后它自己的窗口可以被安全的关闭

### 默认代理池的运行环境(是已有的,不用你安装,仅在这里列出来)

#### Redis-x64-5.0.14.1

rdbcompression no

#### proxy_pool-2.4.1

redis

DB_CONN = "redis://localhost:6379/0"

TABLE_NAME = "use_proxy"

代理验证目标网站

HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://hfs-be.yunxiao.com"

# 使用方式

python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> \[<是否debug>\]

注意:绝大多数情况下不要打开debug,如果确实要使用debug,请在后面添加"True"参数,debug仅建议在单并发下打开

默认配置: `python Control.py 16 12 10` 占用少量资源!

推荐配置: `python Control.py 64 60 10` 一组并发!下行带宽平均占用1mbps

较高配置: `python Control.py 256 250 10` 压榨带宽!

注意:并发不要太高,cpu单核受不了,代理池受不了,内存还行(256并发占用500mb内存)

双击"Default.bat"可以启动代理池,然后运行默认配置,不过这些都需要您手动关闭

就是这样!

# 更新日志

## 2.1

GetRandomProxy现在拥有更小的开销

优化了日志

修复了SendLoop error会卡住的问题

## 2.0

相比于之前的库,使用asyncio全面重构,并且提供了更适合人类阅读的api

可以管这个库叫attack_hfs_v2)))

玩的开心 :D