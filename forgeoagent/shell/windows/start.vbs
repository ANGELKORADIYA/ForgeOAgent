Set WShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
pythonCmd = "python """ & strPath & "\..\..\start.py"""
WShell.Run pythonCmd, 0, False
