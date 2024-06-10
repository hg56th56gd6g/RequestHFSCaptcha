![AttackHFS](/icons/icon.png)

# 使用方式(win64发布包)

1. 下载发布包并解压

2. 双击文件夹内的"ProxyPool.bat"即可启动代理池

3. 双击同目录下的"Default.bat"即可使用默认配置运行主程序

3. 玩的开心! :D

# 使用方式(通用)

并发数 = 进程数\*(不用代理的协程数+使用代理的协程数)

`python Main.py <不用代理的协程数(int)> <使用代理的协程数(int)> <网络timeout时间(float,秒)> <是否debug(str,True/其他)> <进程数(int)>`

默认配置: `python Main.py 1 3 5 False 1` 试试水!

推荐配置: `python Main.py 2 6 5 False 1` 较低占用!

调试配置: `python Main.py 1 0 5 True 1` debug!

多进程是因为python的gil,如果cpu成为瓶颈可以考虑多进程,多进程永远只是备选

就是这样,接下来是python环境配置和代理池使用!

## 0.

win64发布包里的python环境已经安装了这些库,如果你想新开一个python环境或不使用发布包,请继续阅读

## 1.

python3.11

位置就在win64发布包的根目录的Python文件夹,可以参考默认的

## 2.

安装主程序所需的库

`pip install httpx[brotli,http2,socks]`

## 3.

一个https://github.com/jhao104/proxy_pool的代理池,获取随机代理在http://127.0.0.1:5010/get/

或者你也可以修改Proxy.py来使用你自己的获取随机代理

进入"RequestHFSCaptcha\ProxyPool"安装

`pip install -r requirements.txt`

# 更新日志

## 3.1

1. 为请求错误添加了更多的可恢复机会

2. 增加了一个验证码接口,如果帐号已被注册,则切换到该接口(因重置密码而需要发送手机验证码,需要帐号已被注册)

3. win64发布包中分开了代理池和默认配置运行

## 3.0

1. 请求api同步至好分数手机app

2. 大量稳定性与性能优化

3. 命令行第一个参数现在是(几个并发使用代理)而不是以前的(总共几个并发)

4. 入口点改为Main.py并内置了多进程支持,充分利用多个核心

需注意:由于好分数对ip做了限制(仍然是那个http 451问题),可能会有大部分请求都被451了,目前唯一的解决办法就是使用高质量代理,因为这个问题即使是在app上的普通用户也会有

5. win64发布包使用cmd脚本代替exe

## 2.5

1. 优化了Sender

(451必须一直重试,如果直接等待较长一段时间会被关闭服务)

2. 优化了GetSvgCaptcha,解析部分更改为svg标准,并匹配了好分数新的字体,以及更易于理解的代码

## 2.4

1. 优化了GetSvgCaptcha性能

2. 优化了代理

3. 优化了Sender,上个版本的改动效果不佳,又大改了一次,这次效果不错,并且每个并发的资源占用显著降低了

(如果你的cpu成为瓶颈,请考虑开多进程)

ps:有一个问题一直存在,就是captcha(和with svg)请求出一个451状态码(并不是错误)

这时候json解析报错,此连接销毁(然而并不是连接问题),浪费了大量资源

现在这个问题已经修复,其他的错误码(403,400等)确实是错误

4. 其他优化

5. 更换了代理池的抓取/检查间隔,更新了代理池的稻壳ip

6. 修改默认timeout为5秒

## 2.3

1. 取消了各种接收信号退出的机制,在win64的Default.exe和ProxyPool.exe里使用job来保证子进程结束

2. 真的解决了代理池里抓不到代理导致cpu飙升的bug了,之前在报错的时候,会直接跳过休眠

现在如果还是cpu飙升,可能是因为你自己的ip被好分数ban了,然后那个Sender报错,然后就一直新建连接,再报错...

解决方法:全部使用代理即可

3. 可以通过环境变量"HFS_COMMAND_CONFIG"修改默认配置了(仅win64发布包),将Control.py的命令行复制过去即可

例如默认配置: "16 15 10"

你需要输入命令"set HFS_COMMAND_CONFIG=..\Python\python Control.py 16 15 10"

(如果没找到这个环境变量,则使用默认配置)

4. 优化了Sender请求逻辑,避免了很多连接的开销,在充分利用match的基础上充分利用connect

(隐含的好处还有降低代理池压力,更充分的利用每一个代理,以及可以更高并发)

5. 优化了log

6. roleType均衡,比如总16,代理12;会有2学生+非代理,2家长+非代理,6学生+代理,6家长+代理

7. 将win64发布包里代理池的主程序改为c编写,少开一个python进程)))

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