#include <windows.h>
#include <stdint.h>
#include "utils.h"
void ProxyPoolMain(void){
    Name="[ProxyPool]";
    //判断命令行最后一个参数是不是"-"(是否使用无(单)窗口模式)
    LPSTR line=GetCommandLineA();
    uint8_t flag;
    while(*line)
        line++;
    if(*(line-1) == '-'){
        flag=1;
        //子进程句柄全部重定向到nul
        si.hStdInput=CreateFileA("nul",GENERIC_ALL,0,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
        if(si.hStdInput == INVALID_HANDLE_VALUE)
            ErrorExitNoPause("CreateFile");
        if(SetHandleInformation(si.hStdInput,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE
        )==0)ErrorExitNoPause("SetHandleInformation");
        si.dwFlags|=STARTF_USESTDHANDLES;
        si.hStdOutput=si.hStdInput;
        si.hStdError=si.hStdInput;
    }else{
        flag=0;
        //子进程要创建新控制台
        cf|=CREATE_NEW_CONSOLE;
    }

    #define SUBPROCESS_COUNT (3)
    #define job (ph[SUBPROCESS_COUNT])
    HANDLE ph[SUBPROCESS_COUNT+1];
    #define REDIS_CMD "redis-server.exe redis.windows.conf"
    Print("start redis\n");
    Hchdir("ProxyPool\\Redis-x64-5.0.14.1\\");
    if(flag){
        job=Hckj();
        ph[0]=Hckp(REDIS_CMD,job);
    }else{
        Hcdp(REDIS_CMD);
    }

    Print("start schedule and server\n");
    Hchdir("..\\proxy_pool-2.4.1\\");
    #define SCHEDULE_CMD "..\\..\\Python\\python.exe proxyPool.py schedule"
    #define SERVER_CMD "..\\..\\Python\\python.exe proxyPool.py server"
    if(flag){
        ph[1]=Hckp(SCHEDULE_CMD,job);
        ph[2]=Hckp(SERVER_CMD,job);
    }else{
        Hcdp(SCHEDULE_CMD);
        Hcdp(SERVER_CMD);
    }
    Print("ok\n");

    if(flag){
        //作为监工进程的模式(正常应该是直接被结束而不是退出这个函数)
        Hwkp(ph,SUBPROCESS_COUNT);
        ExitNoPause("abort\n");
    }else{
        //为每个服务新建控制台的模式(直接退出)
        ExitNoPause("");
    }
}