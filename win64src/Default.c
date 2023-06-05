#include <windows.h>
#include <stdint.h>
#include "utils.h"
void DefaultMain(void){
    Name="[Default]";
    //子进程们的句柄
    #define SUBPROCESS_COUNT (2)
    #define job (ph[SUBPROCESS_COUNT])
    HANDLE ph[SUBPROCESS_COUNT+1];
    job=Hckj();

    //运行ProxyPool,无窗口模式
    ph[0]=Hckp("ProxyPool.exe -",job);
    //运行Attacker
    Hchdir("Attacker\\");

    {
        //尝试获取替代的默认参数,如果失败则使用默认参数
        #define CMD "..\\Python\\python Control.py "
        #define LEN (sizeof(CMD)-1)
        #define DEFAULT "16 16 10"
        #define LEN_DEF (sizeof(DEFAULT))
        LPSTR line;
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
            ErrorExit("LocalAlloc");
        CopyMemory(line,CMD,LEN);
        if(flag){
            if(GetEnvironmentVariableA("HFS_COMMAND_CONFIG",line+LEN,temp)==0)
                ErrorExit("GetEnvironmentVariable");
        }else{
            CopyMemory(line+LEN,DEFAULT,LEN_DEF);
        }
        #undef CMD
        #undef LEN
        #undef DEFAULT
        #undef LEN_DEF

        ph[1]=Hckp(line,job);
        LocalFree(line);
    }

    Hwkp(ph,SUBPROCESS_COUNT);
    Exit("now you can close this window\n");
}