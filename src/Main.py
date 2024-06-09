#-*- coding:utf-8 -*-
import logging, logging.handlers


def Worker(count, proxy, timeout, log_level, log_queue, result, status):
    import Control
    log = logging.getLogger("RequestHFSCaptcha")
    log.setLevel(log_level)
    log_format = logging.Formatter(
        "[Worker_%(process)d]%(message)s",
        "%Y.%m.%d.%H.%M.%S"
    )
    log_output = logging.handlers.QueueHandler(log_queue)
    log_output.setFormatter(log_format)
    log.addHandler(log_output)
    r = Control.Main(count, proxy, timeout, status)
    result.value = r
    log.debug(f"Control exit, result={r}, u64={result.value}")
    log_queue.close()
    log_queue.join_thread()


def Main():
    import multiprocessing, sys
    #解析命令行<几个并发不用代理> <几个并发使用代理> <timeout(秒)> <是否debug(True/)> <几个进程>
    count = int(sys.argv[1])
    proxy = int(sys.argv[2])
    count += proxy
    timeout = float(sys.argv[3])
    log_level = logging.DEBUG if sys.argv[4] == "True" else logging.INFO
    #日志
    log_w = logging.getLogger("RequestHFSCaptcha_Wrapper")
    log_w.setLevel(log_level)
    log_format = logging.Formatter(
        "[%(asctime)s][%(levelname)s]%(message)s",
        "%Y.%m.%d.%H.%M.%S"
    )
    log_output = logging.StreamHandler(sys.stdout)
    log_output.setFormatter(log_format)
    log_w.addHandler(log_output)
    log_queue = multiprocessing.Queue()
    log_queue_listener = logging.handlers.QueueListener(
        log_queue,
        log_output,
        respect_handler_level = True
    )
    log_queue_listener.start()
    #启动
    log_w.debug(f"args: {sys.argv}")
    log_w.info("Loading...")
    status = multiprocessing.Value("B", lock = False)
    status.value = 1
    subps = []
    for p in range(int(sys.argv[5])):
        r = multiprocessing.Value("Q", lock = False)
        p = multiprocessing.Process(
            target = Worker,
            daemon = True,
            name = f"Worker_{p}",
            args = (count, proxy, timeout, log_level, log_queue, r, status)
        )
        p.start()
        log_w.debug(f"start process: {p.pid}")
        subps.append((p, r))
    log_w.info("Running, input enter to exit...")
    #等待
    while True:
        if sys.stdin.read(1) == "\n":
            break
    log_w.info("Exiting...")
    status.value = 0
    #退出
    result = 0
    for p, r in subps:
        p.join()
        log_w.debug(f"close process: {p.pid}")
        p.close()
        result += r.value
    log_queue_listener.stop()
    log_w.info(f"requested {result} captcha...")


if __name__=="__main__":
    Main()