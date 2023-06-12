#define ProgramName "[Default]"
#include <windows.h>
#include <stdint.h>
#include "utils.h"
void DefaultMain(void){
    //子进程们的句柄
    #define SUBPROCESS_COUNT (2)
    #define job (ph[SUBPROCESS_COUNT])
    HANDLE ph[SUBPROCESS_COUNT+1];
    job=CreateKillerJob();

    //运行ProxyPool,无窗口模式
    ph[0]=CreateKillerProcess("ProxyPool -",job,0,0,0);
    //运行Attacker
    Chdir("Attacker\\");

    {
        //尝试获取替代的默认参数
        DWORD temp=GetEnvironmentVariableA("HFS_COMMAND_CONFIG",0,0);
        if(temp==0){
            //使用默认参数
            ph[1]=CreateKillerProcess("..\\Python\\python Control.py 16 15 5",job,0,0,0);
        }else{
            //给环境变量的值分配内存
            LPSTR line=LocalAlloc(LMEM_FIXED,temp);
            if(line==0)
                ErrorExit("LocalAlloc");
            if(GetEnvironmentVariableA("HFS_COMMAND_CONFIG",line,temp)==0)
                ErrorExit("GetEnv");
            ph[1]=CreateKillerProcess(line,job,0,0,0);
            LocalFree(line);
        }
    }

    WaitForKillerJob(ph,SUBPROCESS_COUNT);
    Abort();
}