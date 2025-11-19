# This script creates a shortcut for start.vbs on the desktop.

# Define the path to the VBScript file
$VBScriptPath = Join-Path $PSScriptRoot "start.vbs"

# Define the path to the desktop
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Define the shortcut path
$ShortcutPath = Join-Path $DesktopPath "start.lnk"

# Create a Shell object
$Shell = New-Object -ComObject WScript.Shell

# Create a shortcut object
$Shortcut = $Shell.CreateShortcut($ShortcutPath)

# Set the target path of the shortcut
$Shortcut.TargetPath = $VBScriptPath

# Save the shortcut
$Shortcut.Save()

# Set the hotkey for the shortcut (e.g., Ctrl + Alt + S)
$Shortcut.Hotkey = "CTRL+ALT+S"


Write-Host "Shortcut for start.vbs created on the desktop."
