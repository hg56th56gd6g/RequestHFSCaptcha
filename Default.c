#define HProgramName "[Default]"
#include <windows.h>
#include <stdint.h>
#include "utils.h"
void DefaultMain(void){
    UtilsInit();
    //子进程们的句柄
    #define SUBPROCESS_COUNT (2)
    HANDLE ph[SUBPROCESS_COUNT],job=CreateKillerJob();

    //运行ProxyPool,无窗口模式
    Hchdir("ProxyPool\\");
    ph[0]=CreateKillerProcess("main.exe -",job);

    //运行Attacker
    Hchdir("..\\Attacker\\");
    //尝试获取替代的默认参数,如果失败则使用默认参数
    #define CMD "..\\Python\\python Control.py "
    #define LEN (sizeof(CMD)-1)
    #define DEFAULT "16 16 10"
    #define LEN_DEF (sizeof(DEFAULT))
    LPSTR line=(CMD DEFAULT);
    DWORD temp=GetEnvironmentVariableA("HFS_COMMAND_CONFIG",0,0);
    uint8_t flag;
    if(temp==0){
        flag=0;
        temp=LEN_DEF;
    }else{
        flag=1;
    }
    //命令行的尺寸是CMD的长度(不包括0)+环境变量HFS_COMMAND_CONFIG的长度(包括0)
    line=LocalAlloc(LMEM_FIXED,LEN+temp);
    if(line==0)
        ErrorExit("LocalAllocError\n");
    CopyMemory(line,CMD,LEN);
    if(flag){
        temp=GetEnvironmentVariableA("HFS_COMMAND_CONFIG",line+LEN,temp);
        if(temp==0)
            ErrorExit("GetEnvironmentVariableError\n");
    }else{
        CopyMemory(line+LEN,DEFAULT,LEN_DEF);
    }
    #undef CMD
    #undef LEN
    #undef DEFAULT
    #undef LEN_DEF
    ph[1]=CreateKillerProcess(line,job);
    LocalFree(line);

    WaitForKillerGroup(ph,job,SUBPROCESS_COUNT);
    Exit("now you can close this window\n");
}