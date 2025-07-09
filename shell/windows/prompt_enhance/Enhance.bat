@echo off
setlocal

:: Get text from clipboard
for /f "delims=" %%i in ('powershell -command "Get-Clipboard"') do set "SELECTED_TEXT=%%i"

:: Check if clipboard is empty
if "%SELECTED_TEXT%"=="" (
    exit /b 1
)

:: Call Python script with clipboard text
for /f "delims=" %%r in ('python "A:\@Coding\@Done Projects\ForgeOAgent\main.py" "%SELECTED_TEXT%"') do set "RESULT=%%r"
echo %RESULT%
:: Check result and copy back to clipboard
if not "%RESULT%"=="" (
    echo %RESULT% | clip
    @REM powershell -command "New-BurntToastNotification -Text 'Success', 'Enhanced prompt copied to clipboard'" 2>nul
) else (
    @REM powershell -command "New-BurntToastNotification -Text 'Error', 'Failed to enhance prompt'" 2>nul
    exit /b 1
)
timeout /t 10 >nul