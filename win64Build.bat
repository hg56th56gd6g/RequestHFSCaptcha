@echo off
::python runtime ues "embed amd64" version
::install pip "https://bootstrap.pypa.io/get-pip.py"
::"%EMBED_PYTHON_PATH%\python" get-pip.py

::use mingw llvm clang msvcrt x64 to build .c file
::"%MINGW_PATH%\clang" -shared %CLANG_OPTION% src\*.c -o build\Attacker\*.*
::use "-e <your main function name(must be not 'main')> -nostartfiles" to get smaller exe
set CLANG_OPTION=-O3 -m64 -nostartfiles -flto -ffunction-sections -fdata-sections -Wl,--gc-sections,--strip-all,-O3

::rebuild
rmdir build\ /s /q
mkdir build\Attacker\
mkdir build\ProxyPool\
mkdir build\Python\
::copy src\*.py to build\Attacker\*.py
copy /b /v src\Control.py build\Attacker\Control.py
copy /b /v src\Sender.py build\Attacker\Sender.py
copy /b /v src\GetRandomProxy.py build\Attacker\GetRandomProxy.py
copy /b /v src\GetSvgCaptcha.py build\Attacker\GetSvgCaptcha.py
copy /b /v src\GetRandomPhone.py build\Attacker\GetRandomPhone.py
::copy win64\ProxyPool\* to build\ProxyPool\*
xcopy win64\ProxyPool build\ProxyPool /e /v /h /q
::copy win64\Python\* to build\Python\*
xcopy win64\Python build\Python /e /v /h /q
::build "icons\icon.ico" with "icons\icon.rc" to "build\icon.o"
"%MINGW_PATH%\windres" --target pe-x86-64 --input icons\icon.rc --output build\icon.o
::build "win64\Default.c" with "build\icon.o" to "build\Default.exe"
"%MINGW_PATH%\clang" -e DefaultMain %CLANG_OPTION% win64\Default.c build\icon.o -o build\Default.exe
del build\icon.o
::build "win64\ProxyPool.c" to "build\ProxyPool\main.exe"
"%MINGW_PATH%\clang" -e ProxyPoolMain %CLANG_OPTION% win64\ProxyPool.c -o build\ProxyPool\main.exe
pause