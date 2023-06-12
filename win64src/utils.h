#ifdef Hdll
    #define HutilsAPI __declspec(dllexport)
#else
    #define HutilsAPI __declspec(dllimport)
#endif
#define HutilsCall __stdcall

#include <windows.h>
#include <stdint.h>

HutilsAPI void HutilsCall Hp(LPSTR name,LPSTR str);
#define Print(str) Hp(ProgramName,str)

#define HE_PRINT (1)
#define HE_ERROR (2)
HutilsAPI void HutilsCall He(LPSTR name,LPSTR str,uint8_t flags,DWORD code);
#define Hexit(str,flags,code) He(ProgramName,str,flags,code)
HutilsAPI void HutilsCall Ee(LPSTR name,LPSTR str);
#define ErrorExit(str) Ee(ProgramName,str)
HutilsAPI void HutilsCall Ab(LPSTR name);
#define Abort() Ab(ProgramName)
HutilsAPI void HutilsCall Ex(LPSTR name,LPSTR str);
#define Exit(str) Ex(ProgramName,str)


HutilsAPI void HutilsCall Hc(LPSTR dir,LPSTR name);
#define Chdir(dir) Hc(dir,ProgramName)

HutilsAPI HANDLE HutilsCall Hj(LPSTR name);
#define CreateKillerJob() Hj(ProgramName)

HutilsAPI HANDLE HutilsCall Hk(LPSTR cmd,HANDLE job,DWORD cf,HANDLE i,HANDLE o,LPSTR name);
#define CreateKillerProcess(cmd,job,cf,i,o) Hk(cmd,job,cf,i,o,ProgramName)

HutilsAPI void HutilsCall Hw(HANDLE *ph,DWORD count,LPSTR name);
#define WaitForKillerJob(ph,count) Hw(ph,count,ProgramName)