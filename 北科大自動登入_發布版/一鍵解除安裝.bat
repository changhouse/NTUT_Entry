@echo off
echo ===================================================
echo         北科大自動登入系統 - 一鍵解除安裝
echo ===================================================
echo.
echo 即將清除所有自動登入設定與暫存檔案...
pause
echo.
echo [1/3] 正在停止背景服務...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo [2/3] 正在移除開機自動啟動設定...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "NTUT_AutoLogin" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v "StartupDelayInMSec" /f >nul 2>&1
echo [3/3] 正在刪除虛擬環境與帳密資料...
cd /d "%~dp0"
if exist ".env" del /f /q ".env"
if exist "server.log" del /f /q "server.log"
if exist ".venv" rmdir /s /q ".venv"
echo.
echo ===================================================
echo   系統設定已全部清除成功！
echo ===================================================
echo.
echo 【最後一步】請手動移除 Chrome 擴充功能：
echo 1. 打開 Chrome 瀏覽器，網址列輸入 chrome://extensions/
echo 2. 找到 北科大自動登入輔助，點擊 移除
echo.
echo 此資料夾已經完全乾淨，您可以直接將整個資料夾丟進資源回收桶了。
pause
