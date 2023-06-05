#ifdef Hdll
    #define HutilsAPI __declspec(dllexport)
#else
    #define HutilsAPI __declspec(dllimport)
#endif
#include <windows.h>
#include <stdint.h>
//创建进程(popen)的设置
HutilsAPI STARTUPINFOA si;
HutilsAPI DWORD cf;
HutilsAPI LPSTR Name;
//一个Print函数,将字符串前面加上HProgramName,然后打印到stdout
HutilsAPI void Print(LPSTR str);
//一个exit函数,可选:打印信息,打印Error,暂停10s再退出
#define HE_PRINT (1)
#define HE_PAUSE (2)
#define HE_ERROR (4)
HutilsAPI void Hexit(LPSTR str,uint8_t flags,DWORD code);
//一个Exit宏,打印一个信息,等待10s,并ExitProcess(0)
#define Exit(str) Hexit(str,HE_PRINT|HE_PAUSE,0)
//一个ErrorExit宏,打印一个错误信息,等待10s,并ExitProcess(1)
#define ErrorExit(str) Hexit(str,HE_PRINT|HE_PAUSE|HE_ERROR,1)
//一个ExitNoPause宏,打印一个信息,并ExitProcess(0)
#define ExitNoPause(str) Hexit(str,HE_PRINT,0)
//一个ErrorExitNoPause宏,打印一个错误信息,并ExitProcess(1)
#define ErrorExitNoPause(str) Hexit(str,HE_PRINT|HE_ERROR,1)

//一个chdir函数,更改当前目录
HutilsAPI void Hchdir(LPCSTR dir);
//一个popen函数,可以接收新进程的句柄和主线程的句柄
HutilsAPI void Hpopen(LPSTR cmd,HANDLE *pProcessHandle,HANDLE *pThreadHandle);
//创建一个不在KillerJob里的子进程
#define Hcdp(cmd) Hpopen(cmd,0,0)
//创建一个CloseHandle时结束其中进程的容器KillerJob
HutilsAPI HANDLE Hckj(void);
//创建一个在KillerJob里的子进程
HutilsAPI HANDLE Hckp(LPSTR cmd,HANDLE job);
//等待多个在KillerJob里的进程,直到其中任意进程结束,然后结束KillerJob
HutilsAPI void Hwkp(HANDLE *ph,DWORD count);