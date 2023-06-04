#define HProgramName "[ProxyPool]"
#include <windows.h>
#include <stdint.h>
#include "utils.h"
void ProxyPoolMain(void){
    UtilsInit();
    //判断命令行最后一个参数是不是"-"(是否使用无(单)窗口模式)
    LPSTR line=GetCommandLineA();
    while(*line)
        line++;
    if(*(line-1) == '-'){
        line=(LPSTR)1;
        //子进程句柄全部重定向到nul
        HANDLE file=CreateFileA("nul",GENERIC_ALL,0,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
        if(file==INVALID_HANDLE_VALUE)
            ErrorExitNoPause("CreateFileError\n");
        if(SetHandleInformation(file,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE,HANDLE_FLAG_INHERIT|HANDLE_FLAG_PROTECT_FROM_CLOSE
        )==0)ErrorExitNoPause("SetHandleInformationError\n");
        si.dwFlags|=STARTF_USESTDHANDLES;
        si.hStdInput=file;
        si.hStdOutput=file;
        si.hStdError=file;
    }else{
        line=(LPSTR)0;
        //子进程要创建新控制台
        dwCreationFlags|=CREATE_NEW_CONSOLE;
    }

    #define SUBPROCESS_COUNT (3)
    HANDLE ph[SUBPROCESS_COUNT],job=CreateKillerJob();
    #define REDIS_CMD "redis-server.exe redis.windows.conf"
    Hchdir("Redis-x64-5.0.14.1\\");
    if(line)
        ph[0]=CreateKillerProcess(REDIS_CMD,job);
    else
        CreateDefaultProcess(REDIS_CMD);

    Hchdir("..\\proxy_pool-2.4.1\\");
    #define SCHEDULE_CMD "..\\..\\Python\\python.exe proxyPool.py schedule"
    #define SERVER_CMD "..\\..\\Python\\python.exe proxyPool.py server"
    if(line){
        ph[1]=CreateKillerProcess(SCHEDULE_CMD,job);
        ph[2]=CreateKillerProcess(SERVER_CMD,job);
    }else{
        CreateDefaultProcess(SCHEDULE_CMD);
        CreateDefaultProcess(SERVER_CMD);
    }

    if(line){
        //作为监工进程的模式(正常应该是直接被结束而不是退出这个函数)
        WaitForKillerGroup(ph,job,SUBPROCESS_COUNT);
        ErrorExitNoPause("ErrorExit...\n");
    }else{
        //为每个服务新建控制台的模式(直接退出)
        CloseHandle(job);
        ExitNoPause("OK\n");
    }
}