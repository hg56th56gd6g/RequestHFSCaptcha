@echo off
::python runtime ues "embed amd64" version
::install pip "https://bootstrap.pypa.io/get-pip.py"
::"%EMBED_PYTHON_PATH%\python" get-pip.py

::use mingw llvm clang msvcrt x64 to build .c file
::"%MINGW_PATH%\clang" -shared %CLANG_OPTION% src\*.c -o build\Attacker\*.*
::use "-e <your main function name(must be not 'main')> -nostartfiles" to get smaller exe
set CLANG_OPTION=-Oz -m64 -nostartfiles -flto -ffunction-sections -fdata-sections -Wl,--gc-sections,--strip-all,-O3

::rebuild
rmdir build\ /s /q
mkdir build\Attacker\
rmdir lib\ /s /q
mkdir lib\
::copy src\*.py to build\Attacker\*.py
copy /b /v src\Control.py build\Attacker\Control.py
copy /b /v src\Sender.py build\Attacker\Sender.py
copy /b /v src\Proxy.py build\Attacker\Proxy.py
copy /b /v src\GetSvgCaptcha.py build\Attacker\GetSvgCaptcha.py
copy /b /v src\Phone.py build\Attacker\Phone.py
::copy win64runtime\* to build\*
xcopy win64runtime build /e /v /h /q
::build "utils.c" to "build\utils.dll" and "lib\utils.lib"
"%MINGW_PATH%\clang" -shared -e DllMain %CLANG_OPTION% win64src\utils.c -o build\utils.dll -D"Hdll" -Wl,--out-implib,"lib\utils.lib"
::build "icons\icon.ico" with "icons\icon.rc" to "lib\icon.o"
"%MINGW_PATH%\windres" --target pe-x86-64 --input icons\icon.rc --output lib\icon.o
::build "win64src\Default.c" with "lib\icon.o" to "build\Default.exe", link "utils.dll"
"%MINGW_PATH%\clang" -e DefaultMain %CLANG_OPTION% win64src\Default.c lib\icon.o -o build\Default.exe -L"lib" -l"utils"
::build "win64src\ProxyPool.c" to "build\ProxyPool.exe", link "utils.dll"
"%MINGW_PATH%\clang" -e ProxyPoolMain %CLANG_OPTION% win64src\ProxyPool.c -o build\ProxyPool.exe -L"lib" -l"utils"
pause