@echo off
REM Workday Activity Logger - Uninstall Script

echo ============================================================
echo  Workday Activity Logger - Uninstall
echo ============================================================
echo.

REM Remove Windows startup task
echo Removing startup task...
schtasks /delete /tn "diary-ai" /f 2>nul
if errorlevel 1 (
    echo   No startup task found (already removed or never installed).
) else (
    echo   Startup task removed.
)
echo.

REM Remove venv\Scripts from user PATH
echo Removing diary-ai from PATH...
powershell -Command "$s='%~dp0venv\Scripts'; $p=[Environment]::GetEnvironmentVariable('PATH','User'); $n=($p -split ';' | Where-Object {$_ -ne $s}) -join ';'; [Environment]::SetEnvironmentVariable('PATH',$n,'User'); Write-Host 'PATH updated.'"
echo.

echo ============================================================
echo  Done. diary-ai will no longer start at login.
echo  The project files and logs have NOT been deleted.
echo ============================================================
echo.
pause
