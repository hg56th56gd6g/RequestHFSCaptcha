![AttackHFS](/icons/icon.png)

# 使用方式(win64发布包)

1. 下载发布包并解压

2. 双击文件夹内的"Default.exe"即可启动代理池(无窗口模式),然后运行默认配置(此时应只有一个窗口,关闭它会关闭主程序和代理池)

3. 玩的开心! :D

# 使用方式(通用)

python Control.py <协程并发数> <几个并发使用代理> <网络timeout时间(秒)> \[<是否debug>\]

注意:绝大多数情况下不要打开debug,如果确实要使用debug,请在后面添加"True"参数,debug仅建议在单并发下打开

默认配置: `python Control.py 16 16 10` 占用少量资源!

推荐配置: `python Control.py 64 60 10` 一组并发!

较高配置: `python Control.py 256 250 10` 压榨带宽!

调试配置: `python Control.py 1 0 10 True` debugggggggggggggggggggggg!

注意:并发不要太高,cpu单核受不了,代理池受不了,内存还行(256并发占用500mb内存)

就是这样,接下来是python环境配置和代理池使用!

## 0.

win64发布包里的python环境已经安装了这些库,如果你想新开一个python环境或不使用发布包,请继续阅读

## 1.

python3.8+(推荐3.10以上,这是我的运行环境)

位置就在win64发布包的根目录的Python文件夹,可以参考默认的

## 2.

在1.的python环境里`pip install httpx[brotli,http2,socks]`,这是主程序需要的库

## 3.

一个https://github.com/jhao104/proxy_pool的代理池,获取随机代理在http://127.0.0.1:5010/get/

或者你也可以修改GetRandomProxy.py来使用你自己的获取随机代理

### 在win64发布包里手动开启代理池

在win64的二进制文件里有提供默认代理池的运行环境

如果你想新开一个python环境(跟2.一样),需要进入"RequestHFSCaptcha\ProxyPool"输入命令`pip install -r requirements.txt`

之后的每次运行你只需要运行"ProxyPool.exe"即可运行代理池,这会新建三个cmd窗口,不要关闭它们,除非你需要关闭代理池

命令行输入`ProxyPool.exe -`可以不新建三个窗口运行代理池(命令行的最后一个字符是"-"即可,后面不要加空格)

注:在无窗口模式下ProxyPool.exe不会主动退出,不要关闭它的窗口,除非你需要关闭代理池

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

## 2.3

1. 取消了各种接收信号退出的机制,在win64的Default.exe和ProxyPool.exe里使用job来保证子进程结束

2. 真的解决了代理池里抓不到代理导致cpu飙升的bug了,之前在报错的时候,会直接跳过休眠

现在如果还是cpu飙升,可能是因为你自己的ip被好分数ban了,然后那个Sender报错,然后就一直新建连接,再报错...

解决方法:全部使用代理即可

3. 可以通过环境变量"HFS_COMMAND_CONFIG"修改默认配置了(仅win64发布包),格式: "[<协程并发数> <几个并发使用代理> <网络timeout时间(秒)>]"

例如默认配置: "16 16 10"

你需要输入命令"set HFS_COMMAND_CONFIG=16 16 10"

(如果没找到这个环境变量,则使用默认配置,其中的内容其实会原封不动传给Control.py)

4. 优化了Sender请求逻辑,避免了很多连接的开销,在充分利用match的基础上充分利用connect

(隐含的好处还有降低代理池压力,更充分的利用每一个代理,以及可以更高并发)

5. 将默认配置修改为全部使用代理

6. roleType均衡,比如总16,代理12;会有2学生+非代理,2家长+非代理,6学生+代理,6家长+代理

7. 将win64发布包里代理池的主程序改为c编写,少开一个python进程)))

8. 优化了log

## 2.2

在win64发布包里你可以不用安装python和执行两条pip install了,已经帮你把所有运行环境打包完毕

现在代理池里抓不到代理不会导致cpu飙升了(此协程休眠10s,不影响其他协程进行除获取代理外的操作,如果其他协程也获取代理,一样会被休眠)

不再打印错误到log,99%都是代理报错的

可以选择不开启代理池环境的三个控制台窗口了,节省你的任务栏空间,同时防止误触关闭代理池

Sender(对象独立,内部线程不安全),GetSvgCaptcha(不需要更改模块级变量),GetRandomPhone(不需要更改模块级变量(random其实不是线程安全的,但这里只是需要随机数,安不安全无所谓)),GetRandomProxy(代理池线程安全)是线程安全的,其他的建议视作线程不安全的

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