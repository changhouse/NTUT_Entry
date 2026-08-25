import keyring
import getpass
from dotenv import set_key, unset_key
from pathlib import Path

SERVICE_NAME = "NTUT_AutoLogin"
env_path = Path(__file__).parent / ".env"
key_path = Path(__file__).parent / "secret.key"

def main():
    print("===================================================")
    print("         北科大自動登入系統 - 憑證設定")
    print("===================================================")
    print("請輸入您的學號與密碼 (密碼將會加密儲存於系統憑證管理員)：")
    username = input("請輸入學號: ")
    password = getpass.getpass("請輸入密碼 (輸入時不會顯示字元): ")

    # 將密碼存入 Windows 憑證管理員
    keyring.set_password(SERVICE_NAME, username, password)

    # .env 只存帳號，不存任何密碼
    env_path.touch(exist_ok=True)
    unset_key(str(env_path), "NTUT_PASSWORD")
    unset_key(str(env_path), "NTUT_PASSWORD_ENC")
    set_key(str(env_path), "NTUT_USERNAME", username)

    # 清理舊版遺留的 secret.key
    if key_path.exists():
        key_path.unlink()
        print("已移除舊版金鑰檔案 (secret.key)")

    print("\n憑證已安全儲存於 Windows 憑證管理員！")
    print("===================================================")

if __name__ == "__main__":
    main()
