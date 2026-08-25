import json, base64, os, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# 強制將輸出導向檔案，避免無黑視窗時崩潰
sys.stdout = open(str(Path(__file__).parent / "server.log"), "a", encoding="utf-8")
sys.stderr = sys.stdout
sys.stdin = open(os.devnull, 'r')

print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- 伺服器超極速啟動 (等待請求) ---", flush=True)

# 延遲載入 (Lazy Loading) 變數
_ocr = None
_cv2 = None
_np = None

SERVICE_NAME = "NTUT_AutoLogin"

class CaptchaHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://nportal.ntut.edu.tw')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        global _ocr, _cv2, _np

        # Origin 驗證：只接受北科大網站或本機 Chrome 擴充功能的請求
        origin = self.headers.get('Origin', '')
        if origin != 'https://nportal.ntut.edu.tw' and not origin.startswith('chrome-extension://'):
            self.send_response(403)
            self.end_headers()
            return

        # 只有在「第一次」真的要算驗證碼時，才把肥大的 AI 套件載入記憶體
        if _ocr is None:
            print(f"[{time.strftime('%H:%M:%S')}] 開始載入 ddddocr 與 OpenCV (冷啟動)...", flush=True)
            import ddddocr
            import cv2 as cv
            import numpy as np
            _cv2 = cv
            _np = np
            _ocr = ddddocr.DdddOcr(show_ad=False)
            print(f"[{time.strftime('%H:%M:%S')}] 載入完畢", flush=True)

        try:
            content_length = int(self.headers['Content-Length'])
            if content_length > 1048576:  # 1MB limit for DoS protection
                self.send_response(413)
                self.end_headers()
                return

            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            b64_data = data.get("image", "").split(",")[-1]
            img_bytes = base64.b64decode(b64_data)

            nparr = _np.frombuffer(img_bytes, _np.uint8)
            img = _cv2.imdecode(nparr, _cv2.IMREAD_COLOR)

            gray = _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)
            _, binary = _cv2.threshold(gray, 150, 255, _cv2.THRESH_BINARY_INV)
            processed_bytes = _cv2.imencode('.png', binary)[1].tobytes()

            captcha_text = _ocr.classification(processed_bytes)
            print(f"[{time.strftime('%H:%M:%S')}] 辨識結果: {captcha_text}", flush=True)

            # 從 .env 讀取帳號，密碼從 Windows 憑證管理員讀取
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=Path(__file__).parent / ".env")
            USERNAME = os.getenv("NTUT_USERNAME", "").strip()

            PASSWORD = ""
            if USERNAME:
                try:
                    import keyring
                    pw = keyring.get_password(SERVICE_NAME, USERNAME)
                    if pw:
                        PASSWORD = pw
                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] 密碼讀取失敗: {e}", flush=True)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://nportal.ntut.edu.tw')
            self.end_headers()

            response = {
                "username": USERNAME,
                "password": PASSWORD,
                "captcha": captcha_text
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] 發生錯誤: {e}", flush=True)
            self.send_response(500)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=CaptchaHandler, port=19222):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"[{time.strftime('%H:%M:%S')}] 伺服器正在監聽 port {port}...", flush=True)
    httpd.serve_forever()

if __name__ == '__main__':
    run()