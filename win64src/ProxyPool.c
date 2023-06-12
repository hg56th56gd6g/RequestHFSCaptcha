#define ProgramName "[ProxyPool]"
#include <windows.h>
#include <stdint.h>
#include "utils.h"
void ProxyPoolMain(void){
    #define SUBPROCESS_COUNT (3)
    #define job (ph[SUBPROCESS_COUNT])
    HANDLE nul,ph[SUBPROCESS_COUNT+1];
    job=CreateKillerJob();
    //判断命令行最后一个参数是不是"-"(是否使用无(单)窗口模式)
    LPSTR line=GetCommandLineA();
    while(*line)
        line++;
    if(*(line-1) == '-'){
        //子进程句柄全部重定向到nul
        line=(LPSTR)1;
        nul=CreateFileA("nul",GENERIC_ALL,0,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
        if(nul==INVALID_HANDLE_VALUE)
            ErrorExit("CreateFile");
        if(SetHandleInformation(nul,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE
        )==0)ErrorExit("SetHandleInformation");
    }else{
        //子进程要创建新控制台
        line=(LPSTR)0;
    }

    //启动redis
    Print("start redis\n");
    Chdir("ProxyPool\\Redis-x64-5.0.14.1\\");
    ph[0]=CreateKillerProcess(
        "redis-server redis.windows.conf",
        line?job:0,
        line?0:CREATE_NEW_CONSOLE,
        line?nul:0,
        line?nul:0
    );

    //启动代理池
    Print("start schedule and server\n");
    Chdir("..\\proxy_pool-2.4.1\\");
    ph[1]=CreateKillerProcess(
        "..\\..\\Python\\python proxyPool.py schedule",
        line?job:0,
        line?0:CREATE_NEW_CONSOLE,
        line?nul:0,
        line?nul:0
    );
    ph[2]=CreateKillerProcess(
        "..\\..\\Python\\python proxyPool.py server",
        line?job:0,
        line?0:CREATE_NEW_CONSOLE,
        line?nul:0,
        line?nul:0
    );
    Print("running\n");

    if(line){
        //作为监工进程的模式(正常应该是直接被结束而不是退出这个函数)
        WaitForKillerJob(ph,SUBPROCESS_COUNT);
        Exit("abort\n");
    }
    //为每个服务新建控制台的模式(直接退出)
    Abort();
}