Set WshShell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
enhancePath = scriptDir & "\index.bat"
WshShell.Run chr(34) & enhancePath & chr(34), 0
Set WshShell = Nothing
