import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    print("Root path requested!")
    return "Minimal Flask App is Running!"

# 프로그램이 직접 실행될 때 웹 서버 시작
if __name__ == "__main__":
    # --- 이 블록이 실행되는지 확인하기 위한 로그 ---
    print("--- INSIDE __name__ == '__main__' BLOCK ---")
    # ----------------------------------------------
    port = int(os.environ.get("PORT", 8080))
    print(f"--- Starting Minimal Flask App on port {port} ---")
    app.run(host='0.0.0.0', port=port)
    # app.run()이 정상 작동하면 아래 로그는 보통 보이지 않음
    print("--- Flask App supposedly stopped ---")
else:
    # --- 스크립트가 임포트되었을 경우 확인 (참고용) ---
    print(f"--- SCRIPT LOADED, BUT __name__ IS: {__name__} ---")
    # ----------------------------------------------------
