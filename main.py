import os
import json
import traceback
import logging
from flask import Flask, request, jsonify

# --- Logging Configuration ---
# 기본 로깅 설정: INFO 레벨 이상의 로그를 콘솔에 출력
# 포맷: [시간] [로그레벨] [메시지]
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()] # 콘솔 핸들러 사용
)

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Configuration (Environment Variables Recommended) ---
# Google Chat API가 요청 시 Authorization 헤더에 넣어주는 Bearer 토큰의 일부 또는
# 검증에 사용할 다른 값 (실제 운영에서는 더 안전한 검증 방식 사용 필요)
# 예: os.environ.get("CHAT_AUTH_TOKEN")
# 여기서는 예시로 간단한 문자열 사용 (보안상 좋지 않음)
# !! 중요 !!: 실제 운영 환경에서는 환경 변수 등을 통해 안전하게 관리하고,
#            JWT 토큰 검증 라이브러리(예: google-auth)를 사용하는 것이 강력히 권장됩니다.
EXPECTED_BEARER_TOKEN_PART = os.environ.get("CHAT_AUTH_TOKEN_PART", "YOUR_EXPECTED_SECRET_OR_TOKEN_PART") # 환경 변수에서 읽거나 기본값 사용

# --- Business Logic Function ---
def handle_chat_event_logic(event):
    """
    Google Chat 이벤트 처리 로직.
    Args:
        event (dict): Google Chat에서 받은 이벤트 데이터 (JSON 파싱된 딕셔너리)
    Returns:
        dict: Google Chat API에 보낼 응답 본문 (JSON으로 변환될 딕셔너리)
    """
    event_type = event.get('type')
    space_name = event.get('space', {}).get('name', 'UnknownSpace')
    user_name = event.get('user', {}).get('displayName', 'UnknownUser') # 메시지 이벤트의 경우

    logging.info(f"Handling event type '{event_type}' from space '{space_name}'")

    if event_type == 'MESSAGE':
        message_text = event.get('message', {}).get('text', '').strip()
        logging.info(f"Received message from '{user_name}': '{message_text}'") # 민감 정보 로깅 최소화

        # --- 여기가 챗봇의 응답을 결정하는 핵심 부분 ---
        # TODO: 여기에 Vertex AI 호출 등 실제 챗봇 로직 구현
        # !! 중요 !!: 만약 Vertex AI 호출 등이 시간이 오래 걸린다면 (예: 2-3초 이상),
        #            Google Chat 타임아웃 (보통 30초)이 발생할 수 있습니다.
        #            이런 경우:
        #            1. 빠른 확인 응답 (예: "알겠습니다. 생각 중이니 잠시만 기다려주세요...")을 먼저 보내고,
        #            2. 실제 작업은 백그라운드에서 비동기적으로 처리 (예: Cloud Tasks, Celery, ThreadPoolExecutor 등 사용)한 뒤,
        #            3. 작업 완료 후 Chat API의 messages.create 메서드를 다시 호출하여 결과 메시지를 보내는 것이 좋습니다.
        response_text = f"{user_name}님의 테스트 메시지 확인했습니다. 내용은 '{message_text}'군요." # 간단한 에코백 + 확인 메시지
        # -------------------------------------------------

        response = {'text': response_text}
        return response

    elif event_type == 'ADDED_TO_SPACE':
        logging.info(f"Bot added to space '{space_name}'")
        # 멤버 추가 시 환영 메시지 등을 보낼 수 있습니다.
        # return {'text': '만나서 반갑습니다! 궁금한 점이 있으면 언제든지 물어보세요.'}
        return {} # ADDED_TO_SPACE/REMOVED_FROM_SPACE는 빈 응답을 보내는 것이 일반적

    elif event_type == 'REMOVED_FROM_SPACE':
        logging.info(f"Bot removed from space '{space_name}'")
        return {} # 빈 응답

    else:
        logging.warning(f"Ignoring unknown event type: {event_type}")
        return {} # 알 수 없는 이벤트 타입은 무시하고 빈 응답

# --- Request Handler (Flask Route) ---
@app.route('/', methods=['POST'])
def handle_post_request():
    """
    POST 요청을 받아 검증하고, 챗봇 로직 함수로 넘김
    """
    # 1. Request Verification (보안 강화)
    #    Google Chat 요청인지 간단히 확인 (실제로는 JWT 토큰 검증 권장)
    auth_header = request.headers.get('Authorization')
    is_authorized = False
    if auth_header and auth_header.startswith('Bearer '):
        # 실제 토큰 검증 로직 필요 (예: google-auth 라이브러리 사용)
        # 여기서는 헤더 존재 및 간단한 값 포함 여부만 체크 (예시)
        token = auth_header.split(' ')[1]
        # !! 아래 로직은 예시일 뿐, 실제 환경에서는 훨씬 안전한 검증 필요 !!
        if EXPECTED_BEARER_TOKEN_PART and EXPECTED_BEARER_TOKEN_PART in token: # 매우 기본적인 체크
             is_authorized = True
        # 실제 JWT 검증 예시 (라이브러리 필요):
        # try:
        #     from google.oauth2 import id_token
        #     from google.auth.transport import requests as reqs
        #     audience = "YOUR_CHAT_APP_AUDIENCE" # 설정 필요
        #     id_info = id_token.verify_oauth2_token(token, reqs.Request(), audience)
        #     # 추가 검증 (issuer 등)
        #     is_authorized = True
        # except ValueError as e:
        #     logging.warning(f"Token validation failed: {e}")
        #     is_authorized = False

    if not is_authorized and EXPECTED_BEARER_TOKEN_PART: # 토큰 검증 설정이 있을 때만 검사
         logging.warning("Unauthorized request received.")
         # 401 Unauthorized 또는 403 Forbidden 반환
         return jsonify({'error': 'Unauthorized'}), 401

    # 2. Get JSON Data
    event_data = request.get_json()
    if not event_data:
        logging.error("Error: No data received or not JSON")
        return jsonify({'error': 'Invalid request body, expected JSON'}), 400 # Bad Request

    # 3. Call Logic Function and Handle Potential Errors
    try:
        # 상세 이벤트 로깅은 로직 함수 내부에서 필요한 정보만 하도록 변경
        # logging.debug(f"Received verified event data: {json.dumps(event_data)}") # 필요시 DEBUG 레벨로 전체 로깅

        response_body = handle_chat_event_logic(event_data)
        return jsonify(response_body)

    except Exception as e:
        # 예상치 못한 오류 발생 시 상세 로그 기록 및 일반 오류 응답 반환
        logging.error(f"Error handling event: {e}")
        logging.error(traceback.format_exc()) # 상세 스택 트레이스 로깅
        # 500 Internal Server Error 반환
        return jsonify({'error': 'An internal server error occurred'}), 500

# --- Main Execution Block (for Local Development & Info) ---
if __name__ == "__main__":
    # !! 중요 !!
    # 아래 app.run()은 로컬 개발 및 테스트 용도입니다.
    # 프로덕션 환경(예: Cloud Run, GKE, VM 등)에서는 Gunicorn, uWSGI 같은
    # WSGI 서버를 사용하여 이 Flask 앱을 실행해야 합니다.
    #
    # 예시 (Gunicorn 사용):
    # 1. Gunicorn 설치: pip install gunicorn
    # 2. 실행 명령어 (터미널에서):
    #    gunicorn --bind :$PORT main:app
    #    (main.py 파일의 app 객체를 사용. $PORT는 환경 변수 또는 실제 포트 번호)
    #    Cloud Run에서는 자동으로 PORT 환경 변수를 주입해 줍니다.
    #
    # Dockerfile 예시 (Cloud Run 배포 시):
    # ```Dockerfile
    # FROM python:3.9-slim
    # WORKDIR /app
    # COPY requirements.txt .
    # RUN pip install --no-cache-dir -r requirements.txt
    # COPY . .
    # # PORT 환경 변수는 Cloud Run에서 자동으로 설정됨
    # CMD ["gunicorn", "--bind", ":$PORT", "--workers", "2", "--threads", "4", "main:app"] # Worker/Thread 수는 조정 가능
    # ```
    # (위 Dockerfile 사용 시 requirements.txt 파일에 Flask, Gunicorn 추가 필요)

    port = int(os.environ.get("PORT", 8080))
    logging.info(f"--- Starting Flask Development Server on http://0.0.0.0:{port} ---")
    logging.warning("*** This is a DEVELOPMENT server. Do NOT use it in a production deployment. ***")
    logging.warning("*** Use a WSGI server like Gunicorn instead for production. ***")
    # debug=False가 기본값이며, 프로덕션에서는 절대 True로 설정하지 마세요.
    app.run(host='0.0.0.0', port=port, debug=False)

