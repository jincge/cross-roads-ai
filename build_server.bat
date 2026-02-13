@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
D:\tools\jetbrain\clion\bin\cmake\win\x64\bin\cmake.exe -S . -B cmake-build-debug -G Ninja
D:\tools\jetbrain\clion\bin\cmake\win\x64\bin\cmake.exe --build cmake-build-debug

