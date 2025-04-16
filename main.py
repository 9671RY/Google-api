import os
import json
import traceback
from flask import Flask, request, jsonify

print("--- [DEBUG] main.py script started ---") # 스크립트 시작 로그

print("--- [DEBUG] Creating Flask app instance ---")
app = Flask(__name__)
print("--- [DEBUG] Flask app instance created ---")

# 라우트 정의 직전/직후에 로그 추가
print("--- [DEBUG] Attempting to define route for POST / ---")
@app.route('/', methods=['POST'])
def handle_post_request():
    print("--- POST request received at '/' endpoint! (Simplified Handler) ---")
    return jsonify({'status': 'POST received successfully'}), 200
# 이 로그가 시작 로그에 나타나는지 확인!
print("--- [DEBUG] Route for POST / defined successfully? ---")

# 혹시 모를 GET 라우트도 추가해서 비교 (선택 사항)
# print("--- [DEBUG] Attempting to define route for GET / ---")
# @app.route('/', methods=['GET'])
# def handle_get_request():
#     print("--- GET request received at '/' endpoint! ---")
#     return "Hello from GET request!", 200
# print("--- [DEBUG] Route for GET / defined successfully? ---")


print("--- [DEBUG] Checking if running as main script ---")
if __name__ == "__main__":
    print("--- [DEBUG] Inside __main__ block ---")
    try:
        port = int(os.environ.get("PORT", 8080))
        print(f"--- [DEBUG] Starting Flask server on 0.0.0.0:{port} ---")
        # 운영 환경에서는 debug=False 권장
        app.run(host='0.0.0.0', port=port)
        print("--- [DEBUG] app.run finished (should not happen normally) ---")
    except Exception as e:
        print(f"--- [DEBUG] ERROR in __main__ block: {e}")
        traceback.print_exc()
else:
     print(f"--- [DEBUG] Script imported, __name__ is {__name__} ---")

print("--- [DEBUG] main.py script finished ---") # 메인 블록 밖 로그
