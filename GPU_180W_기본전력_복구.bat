@echo off
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo [!] Requesting Administrative Privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c """%~s0""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
    title GPU Power Limit - 180W (Default)
    echo ========================================================
    echo Restoring NVIDIA GPU Power Limit to 180W (Default)
    echo ========================================================
    echo.
    nvidia-smi -pl 180
    echo.
    echo ========================================================
    nvidia-smi --query-gpu=name,power.limit,temperature.gpu --format=csv
    echo ========================================================
    echo.
    echo [V] 180W Default Power Limit successfully restored!
    timeout /t 5
