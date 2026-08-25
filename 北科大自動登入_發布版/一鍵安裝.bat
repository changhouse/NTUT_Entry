@echo off
echo ===================================================
echo         北科大自動登入系統 - 一鍵安裝程式
echo ===================================================
echo.
cd /d "%~dp0"
echo [1/4] 檢查系統環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請先安裝 Python 並勾選 Add to PATH。
    pause
    exit /b
)
echo.
echo [2/4] 正在建立虛擬環境與安裝核心套件 (請稍候，畫面會顯示安裝進度)...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo 安裝套件完成！
echo.
echo [3/4] 請設定您的北科大入口網站帳號密碼：
.venv\Scripts\python.exe setup_credentials.py
echo.
echo [4/4] 正在設定開機自動啟動...
set "RUN_SCRIPT=%~dp0背景啟動.bat"
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "NTUT_AutoLogin" /t REG_SZ /d "\"%RUN_SCRIPT%\"" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v "StartupDelayInMSec" /t REG_DWORD /d 0 /f >nul
echo.
echo ===================================================
echo   安裝與設定全部完成！
echo ===================================================
echo.
echo 【最後一步】請將擴充功能加入 Chrome：
echo 1. 打開 Chrome 瀏覽器，網址列輸入 chrome://extensions/
echo 2. 開啟右上角的 開發人員模式
echo 3. 點擊左上角 載入未封裝項目
echo 4. 選擇這個資料夾裡面的 chrome_ext 資料夾
echo.
echo 正在為您首次啟動伺服器...
start "" "%RUN_SCRIPT%"
pause
