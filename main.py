import os
from flask import Flask

app = Flask(__name__)

# 아주 기본적인 응답 경로
@app.route('/')
def hello():
    print("Root path requested!") # 요청이 오는지 확인용 로그
    return "Minimal Flask App is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"--- Starting Minimal Flask App on port {port} ---") # 시작 로그 추가
    # 디버그 모드는 Cloud Run에서 보통 사용하지 않음
    app.run(host='0.0.0.0', port=port)
    print("--- Flask App should be running now ---") # app.run()은 보통 블로킹되어 이 줄은 실행 안됨
