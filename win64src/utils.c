#include <windows.h>
#include <stdint.h>
#include "utils.h"
//创建进程(popen)的设置
HutilsAPI STARTUPINFOA si={sizeof(si)};
HutilsAPI DWORD cf=0;
HutilsAPI LPSTR Name;
//初始化stdin和stdout
HANDLE stdin,stdout;
BOOL WINAPI DllMain(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpvReserved){
    if(
        ((stdin=GetStdHandle(STD_INPUT_HANDLE))==INVALID_HANDLE_VALUE)||
        ((stdout=GetStdHandle(STD_OUTPUT_HANDLE))==INVALID_HANDLE_VALUE)
    )return FALSE;
    return TRUE;
}

//一个Print函数,将字符串前面加上Name,然后打印到stdout
HutilsAPI void Print(LPSTR str){
    DWORD len=0;
    while(Name[len])
        len++;
    WriteFile(stdout,Name,len,0,0);
    len=0;
    while(str[len])
        len++;
    WriteFile(stdout,str,len,0,0);
}
//一个exit函数,可选:打印信息,打印Error,暂停10s再退出
HutilsAPI void Hexit(LPSTR str,uint8_t flags,DWORD code){
    if(flags&HE_PRINT)
        Print(str);
    if(flags&HE_ERROR){
        Print("Error\n");
    }
    if(flags&HE_PAUSE){
        Print("auto exit after 10s\n");
        Sleep(10000);
    }
    ExitProcess(code);
}

//一个chdir函数,更改当前目录
HutilsAPI void Hchdir(LPCSTR dir){
    if(SetCurrentDirectoryA(dir)==0)
        ErrorExit("SetCurrentDirectory");
}
//一个popen函数,可以接收新进程的句柄和主线程的句柄
HutilsAPI void Hpopen(LPSTR cmd,HANDLE *pProcessHandle,HANDLE *pThreadHandle){
    PROCESS_INFORMATION pi;
    if(CreateProcessA(0,cmd,0,0,TRUE,cf,0,0,&si,&pi)==0)
        ErrorExit("CreateProcess");
    if(pProcessHandle)
        *pProcessHandle=pi.hProcess;
    else
        CloseHandle(pi.hProcess);
    if(pThreadHandle)
        *pThreadHandle=pi.hThread;
    else
        CloseHandle(pi.hThread);
}
//创建一个CloseHandle时结束其中进程的容器KillerJob
HutilsAPI HANDLE Hckj(void){
    //创建job
    HANDLE job=CreateJobObjectA(0,0);
    if(job==0)
        ErrorExit("CreateJobObject");
    //设置job的信息(job结束时结束进程树内的所有进程)
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION ji;
    ji.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(SetInformationJobObject(job,JobObjectExtendedLimitInformation,&ji,sizeof(ji))==0)
        ErrorExit("SetInformationJobObject");
    return job;
}
//创建一个在KillerJob里的子进程
HutilsAPI HANDLE Hckp(LPSTR cmd,HANDLE job){
    //判断是否以及有CREATE_SUSPENDED这个flag
    uint8_t flag;
    if(cf&CREATE_SUSPENDED){
        flag=1;
    }else{
        flag=0;
        cf|=CREATE_SUSPENDED;
    }
    //创建子进程,初始暂停
    HANDLE hp,ht;
    Hpopen(cmd,&hp,&ht);
    //加入job
    if(AssignProcessToJobObject(job,hp)==0)
        ErrorExit("AssignProcessToJobObject");
    //恢复子进程运行
    if(ResumeThread(ht)!=1)
        ErrorExit("ResumeThread");
    CloseHandle(ht);
    //恢复dwCreationFlags
    if(flag){
        cf&=(~CREATE_SUSPENDED);
    }
    return hp;
}
//等待多个在KillerJob里的进程,直到其中任意进程结束,然后结束KillerJob
HutilsAPI void Hwkp(HANDLE *ph,DWORD count){
    if(WaitForMultipleObjects(count,ph,FALSE,INFINITE)==WAIT_FAILED)
        ErrorExit("WaitForMultipleObjects");
    CloseHandle(ph[count]);
}