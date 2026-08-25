Set WshShell = CreateObject("WScript.Shell")
' 0 代表隱藏視窗執行
WshShell.Run "cmd.exe /c cd /d d:\project\NTUT_Entry && .venv\Scripts\python.exe server.py", 0, False
