![AttackHFS](/icons/icon.png)

# 使用方式(win64发布包)

1. 下载发布包并解压

2. 双击文件夹内的"Default.exe"即可启动代理池(无窗口模式),然后运行默认配置(此时应只有一个窗口,关闭它会关闭主程序和代理池)

3. 玩的开心! :D

# 使用方式(通用)

python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> \[<是否debug>\]

注意:绝大多数情况下不要打开debug,如果确实要使用debug,请在后面添加"True"参数,debug仅建议在单并发下打开

默认配置: `python Control.py 16 12 10` 占用少量资源!

推荐配置: `python Control.py 64 60 10` 一组并发!

较高配置: `python Control.py 256 250 10` 压榨带宽!

调试配置: `python Control.py 1 0 10 True` debugggggggggggggggggggggg!

注意:并发不要太高,cpu单核受不了,代理池受不了,内存还行(256并发占用500mb内存)

就是这样,接下来是python环境配置和代理池使用!

## 1.

python3.8+(推荐3.10以上,这是我的运行环境)

## 2.

在1.的python环境里`pip install httpx[brotli,http2,socks]`,这是主程序需要的库

## 3.

一个https://github.com/jhao104/proxy_pool的代理池,获取随机代理在http://127.0.0.1:5010/get/

或者你也可以修改GetRandomProxy.py来使用你自己的获取随机代理

### 在win64发布包里手动开启代理池

在win64的二进制文件里有提供默认代理池的运行环境,第一次运行前你需要进入"RequestHFSCaptcha\ProxyPool"输入命令`pip install -r requirements.txt`

注:用跟1.一样的python环境就行,或者你愿意新开一个也行

之后的每次运行你只需要输入`python main.py`即可运行代理池,这会新建三个cmd窗口,不要关闭它们,除非你需要关闭代理池

注:加上main.py的有四个窗口,main.py结束后它自己的窗口可以被安全的关闭

输入`python main.py True`可以不新建三个窗口运行代理池

注:在无窗口模式下main.py不会主动退出,不要关闭它的窗口,除非你需要关闭代理池,main.py的进程会作为监工进程与代理池一起结束

### win64默认代理池的运行环境(是已有的,不用你安装,仅在这里列出来)

#### Redis-x64-5.0.14.1

rdbcompression no

#### proxy_pool-2.4.1

redis配置

DB_CONN = "redis://localhost:6379/0"

TABLE_NAME = "use_proxy"

代理验证目标网站

HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://hfs-be.yunxiao.com"

代理池内最小代理数量

POOL_SIZE_MIN = 256

# 更新日志

## 2.2

在win64发布包里你可以不用安装python和执行两条pip install了,已经帮你把所有运行环境打包完毕

现在代理池里抓不到代理不会导致cpu飙升了(此协程休眠10s,不影响其他协程进行除获取代理外的操作,如果其他协程也获取代理,一样会被休眠)

不再打印错误到log,99%都是代理报错的

可以选择不开启代理池环境的三个控制台窗口了,节省你的任务栏空间,同时防止误触关闭代理池

Sender(对象独立),GetSvgCaptcha(不需要更改模块级变量),GetRandomPhone(不需要更改模块级变量(random其实不是线程安全的,但这里只是需要随机数,安不安全无所谓)),GetRandomProxy(代理池线程安全)是线程安全的,其他的建议视作线程不安全的

优化了图标和项目结构

减小了各种文件的尺寸,快说谢谢h5

## 2.1

GetRandomProxy现在拥有更小的开销

优化了日志

修复了SendLoop error会卡住的问题

## 2.0

相比于之前的库,使用asyncio全面重构,并且提供了更适合人类阅读的api

可以管这个库叫attack_hfs_v2)))

玩的开心 :D