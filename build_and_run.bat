@echo off
REM Build and run script for Cross Road AI C++/CLI WinForms app
REM Adjust VC tools path below if your Visual Studio is installed elsewhere.
set VCVARS="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
if not exist %VCVARS% (
  echo Could not find vcvarsall.bat at %VCVARS%
  echo Please update the path in this script to your Visual Studio installation.
  exit /b 1
)
call %VCVARS% x64
REM Clear CL to avoid /EHs being injected by environment
set CL=
REM Compile with C++20 and /clr; compile all src cpp files and main.cpp
cl /nologo /clr /std:c++20 main.cpp src\*.cpp /Fe:cross-road.exe
if exist cross-road.exe (
  echo Built cross-road.exe
  start "" cross-road.exe
) else (
  echo Build failed
)
exit /b 0
