#include <windows.h>
#include <stdint.h>
#include "utils.h"
#define _ErrorExit(name,str) He(name,str,HE_PRINT|HE_ERROR,1)
BOOL WINAPI DllMain(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpvReserved){
    return TRUE;
}

//一个print函数,将字符串前面加上name,然后打印到stdout
HutilsAPI void HutilsCall Hp(LPSTR name,LPSTR str){
    HANDLE stdout=GetStdHandle(STD_OUTPUT_HANDLE);
    if(stdout==INVALID_HANDLE_VALUE)
        return;
    DWORD len=0;
    while(name[len])len++;
    WriteFile(stdout,name,len,0,0);
    len=0;
    while(str[len])len++;
    WriteFile(stdout,str,len,0,0);
}
//一个exit函数,可选:打印信息,打印Error;然后暂停10s再退出
HutilsAPI void HutilsCall He(LPSTR name,LPSTR str,uint8_t flags,DWORD code){
    if(flags&HE_PRINT)
        Hp(name,str);
    if(flags&HE_ERROR)
        Hp(name,"Error\n");
    Hp(name,"auto exit after 10s\n");
    Sleep(10000);
    ExitProcess(code);
}
//一个ErrorExit宏,打印一个错误信息,等待10s,并ExitProcess(1)
HutilsAPI void HutilsCall Ee(LPSTR name,LPSTR str){
    He(name,str,HE_PRINT|HE_ERROR,1);
}
//一个Abort宏,等待10s,并ExitProcess(0)
HutilsAPI void HutilsCall Ab(LPSTR name){
    He(name,0,0,0);
}
//一个Exit宏,打印一个信息,等待10s,并ExitProcess(0)
HutilsAPI void HutilsCall Ex(LPSTR name,LPSTR str){
    He(name,str,HE_PRINT,0);
}

//一个chdir函数,更改当前目录
HutilsAPI void HutilsCall Hc(LPSTR dir,LPSTR name){
    if(SetCurrentDirectoryA(dir)==0)
        _ErrorExit(name,"SetCurrentDirectory");
}
//创建一个CloseHandle时结束其中进程的容器KillerJob
HutilsAPI HANDLE HutilsCall Hj(LPSTR name){
    //创建job
    HANDLE job=CreateJobObjectA(0,0);
    if(job==0)
        _ErrorExit(name,"CreateJobObject");
    //设置job的信息(job结束时结束进程树内的所有进程)
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION ji;
    ji.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(SetInformationJobObject(job,JobObjectExtendedLimitInformation,&ji,sizeof(ji))==0)
        _ErrorExit(name,"SetInformationJobObject");
    return job;
}
//创建一个(可选,在KillerJob里的)子进程
HutilsAPI HANDLE HutilsCall Hk(LPSTR cmd,HANDLE job,DWORD cf,HANDLE i,HANDLE o,LPSTR name){
    //如果要加入job,需要初始暂停
    if(job){
        cf|=CREATE_SUSPENDED;
    }
    //创建子进程
    PROCESS_INFORMATION pi;
    STARTUPINFOA si={sizeof(si)};
    if(i||o)
        si.dwFlags|=STARTF_USESTDHANDLES;
    if(i)
        si.hStdInput=i;
    if(o)
        si.hStdOutput=si.hStdError=o;
    if(CreateProcessA(0,cmd,0,0,TRUE,cf,0,0,&si,&pi)==0)
        _ErrorExit(name,"CreateProcess");
    if(job){
        //加入job
        if(AssignProcessToJobObject(job,pi.hProcess)==0)
            _ErrorExit(name,"AssignProcessToJobObject");
        //恢复子进程运行
        if(ResumeThread(pi.hThread)!=1)
            _ErrorExit(name,"ResumeThread");
    //关闭一些不需要的句柄
    }else{
        CloseHandle(pi.hProcess);
        pi.hProcess=0;
    }
    CloseHandle(pi.hThread);
    return pi.hProcess;
}
//等待多个在KillerJob里的进程,直到其中任意进程结束,然后结束KillerJob,ph数组有count个进程句柄和最后一个job句柄
HutilsAPI void HutilsCall Hw(HANDLE *ph,DWORD count,LPSTR name){
    if(WaitForMultipleObjects(count,ph,FALSE,INFINITE)==WAIT_FAILED)
        _ErrorExit(name,"WaitForMultipleObjects");
    CloseHandle(ph[count]);
}