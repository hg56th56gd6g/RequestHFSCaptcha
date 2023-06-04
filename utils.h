#include <windows.h>
#include <stdint.h>
//创建进程(system)的设置
STARTUPINFOA si={sizeof(si)};
DWORD dwCreationFlags=0;
//初始化stdin和stdout
HANDLE stdin,stdout;
void UtilsInit(void){
    if(
        ((stdin=GetStdHandle(STD_INPUT_HANDLE))==INVALID_HANDLE_VALUE)||
        ((stdout=GetStdHandle(STD_OUTPUT_HANDLE))==INVALID_HANDLE_VALUE)
    )ExitProcess(2);
}

//一个Print宏,将字符串前面加上HProgramName,然后打印到stdout
void Hprint(LPSTR str,DWORD len){
    WriteFile(stdout,HProgramName,sizeof(HProgramName)-1,0,0);
    WriteFile(stdout,str,len,0,0);
}
#define Print(str) Hprint(str,sizeof(str)-1)
//_Exit函数,可选:打印信息,显示GetLastError的错误信息弹窗,暂停10s再退出
#define HE_PRINT (1)
#define HE_PAUSE (2)
#define HE_ERROR (4)
void Hexit(LPSTR str,DWORD len,uint8_t flags,DWORD code){
    if(flags&HE_PRINT)
        Hprint(str,len);
    if(flags&HE_ERROR){
        LPVOID lpMsgBuf;
        FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER|FORMAT_MESSAGE_FROM_SYSTEM|FORMAT_MESSAGE_IGNORE_INSERTS,0,GetLastError(),0,(LPSTR)&lpMsgBuf,0,0);
        MessageBoxA(0,(LPSTR)lpMsgBuf,0,0);
    }
    if(flags&HE_PAUSE){
        Print("auto exit after 10s\n");
        Sleep(10000);
    }
    ExitProcess(code);
}
//一个Exit宏,打印一个信息,等待10s,并ExitProcess(0)
#define Exit(str) Hexit(str,sizeof(str)-1,HE_PRINT|HE_PAUSE,0)
//一个ErrorExit宏,打印一个错误信息,等待10s,并ExitProcess(1)
#define ErrorExit(str) Hexit(str,sizeof(str)-1,HE_PRINT|HE_PAUSE|HE_ERROR,1)
//一个ExitNoPause宏,打印一个信息,并ExitProcess(0)
#define ExitNoPause(str) Hexit(str,sizeof(str)-1,HE_PRINT,0)
//一个ErrorExitNoPause宏,打印一个错误信息,并ExitProcess(1)
#define ErrorExitNoPause(str) Hexit(str,sizeof(str)-1,HE_PRINT|HE_ERROR,1)

//一个chdir函数,更改当前目录
void Hchdir(LPCSTR dir){
    if(SetCurrentDirectoryA(dir)==0)
        ErrorExit("SetCurrentDirectoryError\n");
}
//一个popen函数,可以接收新进程的句柄和pid,以及主线程的句柄和id
void Hpopen(LPSTR cmd,HANDLE *pProcessHandle,HANDLE *pThreadHandle,DWORD *pProcessId,DWORD *pThreadId){
    PROCESS_INFORMATION pi;
    if(CreateProcessA(0,cmd,0,0,TRUE,dwCreationFlags,0,0,&si,&pi)==0)
        ErrorExit("CreateProcessError\n");
    if(pProcessHandle)
        *pProcessHandle=pi.hProcess;
    else
        CloseHandle(pi.hProcess);
    if(pThreadHandle)
        *pThreadHandle=pi.hThread;
    else
        CloseHandle(pi.hThread);
    if(pProcessId)
        *pProcessId=pi.dwProcessId;
    if(pThreadId)
        *pThreadId=pi.dwThreadId;
}
//创建一个不在KillerJob里的子进程
#define CreateDefaultProcess(cmd) Hpopen(cmd,0,0,0,0)
//创建一个CloseHandle时结束其中进程的容器(是job对象)
HANDLE CreateKillerJob(void){
    //创建job
    HANDLE job=CreateJobObjectA(0,0);
    if(job==0)
        ErrorExit("CreateJobObjectError\n");
    //设置job的信息(job结束时结束进程树内的所有进程)
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION ji;
    ji.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(SetInformationJobObject(job,JobObjectExtendedLimitInformation,&ji,sizeof(ji))==0)
        ErrorExit("SetInformationJobObjectError\n");
    return job;
}
//创建一个在KillerJob里的子进程
HANDLE CreateKillerProcess(LPSTR cmd,HANDLE job){
    //判断是否以及有CREATE_SUSPENDED这个flag
    uint8_t flag;
    if(dwCreationFlags&CREATE_SUSPENDED){
        flag=1;
    }else{
        flag=0;
        dwCreationFlags|=CREATE_SUSPENDED;
    }
    //创建子进程,初始暂停
    HANDLE hp,ht;
    Hpopen(cmd,&hp,&ht,0,0);
    //加入job
    if(AssignProcessToJobObject(job,hp)==0)
        ErrorExit("AssignProcessToJobObjectError\n");
    //恢复子进程运行
    DWORD temp;
    for(;;){
        temp=ResumeThread(ht);
        //错误
        if(temp==((DWORD)-1))
            ErrorExit("ResumeThreadError\n");
        //还没有恢复运行
        if(1<=temp)
            continue;
        break;
    }
    CloseHandle(ht);
    //恢复dwCreationFlags
    if(flag!=0){
        dwCreationFlags&=(~CREATE_SUSPENDED);
    }
    return hp;
}
//等待多个在KillerJob里的进程,直到其中任意进程结束,然后结束KillerJob
void WaitForKillerGroup(HANDLE *ph,HANDLE job,DWORD count){
    if(WaitForMultipleObjects(count,ph,FALSE,INFINITE)==WAIT_FAILED)
        ErrorExit("WaitForMultipleObjectsError\n");
    //然后结束掉job对象
    CloseHandle(job);
}