@echo off
setlocal enabledelayedexpansion

REM Get selected text from clipboard
powershell -command "Get-Clipboard" > temp_clipboard.txt
set /p SELECTED_TEXT=<temp_clipboard.txt
del temp_clipboard.txt

REM Define Python and script paths dynamically based on current dir
set "PYTHON_BIN=python"
set "SCRIPT_PATH=%~dp0..\..\main.py"

REM Get prompt type list using -l and process it
"%PYTHON_BIN%" "%SCRIPT_PATH%" -l > temp_prompt_types.txt
if errorlevel 1 (
    echo Error: Failed to get prompt types
    pause
    exit /b 1
)
REM Process each line of temp_prompt_types.txt, remove "_system_instruction" from name, and output to temp_prompt_types_clean.txt
(for /f "usebackq delims=" %%A in ("temp_prompt_types.txt") do (
    set "line=%%A"
    set "line=!line:_system_instruction=!"
    echo !line!
)) > temp_prompt_types_clean.txt
del temp_prompt_types.txt

REM Use PowerShell GUI for selection (similar to zenity)
powershell -command "& {$types = Get-Content 'temp_prompt_types_clean.txt'; $selected = $types | Out-GridView -Title 'Select Prompt Type' -OutputMode Single; if ($selected) { $selected } else { exit 1 }}" > temp_selected.txt
if errorlevel 1 (
    echo Cancelled: No prompt type selected
    del temp_prompt_types_clean.txt
    if exist temp_selected.txt del temp_selected.txt
    pause
    exit /b 1
)

set /p SELECTED_TYPE=<temp_selected.txt
del temp_selected.txt
del temp_prompt_types_clean.txt

REM Check if selected text exists
if "%SELECTED_TEXT%"=="" (
    echo Error: No text in clipboard
    pause
    exit /b 1
)

REM Call Python script with selected type and selected text
"%PYTHON_BIN%" "%SCRIPT_PATH%" -p "%SELECTED_TYPE%" "%SELECTED_TEXT%" > temp_result.txt
if errorlevel 1 (
    echo Error: Failed to process prompt
    if exist temp_result.txt del temp_result.txt
    pause
    exit /b 1
)

REM Copy result to clipboard
powershell -command "Get-Content temp_result.txt | Set-Clipboard"
del temp_result.txt

echo Success: Prompt processed and copied to clipboard
pause
exit /b 0

:lowercase
REM This function is no longer needed but kept for compatibility
set "%~1=!%~1!"
goto :eof