import os
import json
import traceback # 오류 추적을 위해 추가
from flask import Flask, request, jsonify

# --- 1. Flask 앱 초기화 ---
# Flask 애플리케이션 인스턴스를 생성합니다.
app = Flask(__name__)
print("--- Flask app initialized ---")

# --- 2. 핵심 챗봇 로직 함수 ---
# Google Chat 이벤트를 받아서 처리하고 응답을 생성하는 함수입니다.
def handle_chat_event_logic(event):
    """Google Chat 이벤트 데이터를 받아 처리하고 응답 JSON을 반환합니다."""
    # 수신된 이벤트 데이터 로그 출력 (디버깅용)
    # 실제 운영 시에는 개인 정보 등 민감 데이터 로깅에 주의해야 합니다.
    print(f"Received event: {json.dumps(event, indent=2)}")

    event_type = event.get('type')

    # 메시지 이벤트 처리
    if event_type == 'MESSAGE':
        # 사용자가 보낸 텍스트 (단순화된 접근)
        # 실제로는 event['message']['argumentText'] 등을 확인해야 할 수 있습니다.
        # user_message = event.get('message', {}).get('text', '')
        # print(f"User message: {user_message}") # 사용자 메시지 로그 (필요시)

        # --- 여기가 실제 응답 생성 로직 ---
        # 현재는 고정된 텍스트로 응답합니다.
        # 향후 이 부분에 Vertex AI 호출 등의 로직을 추가할 수 있습니다.
        response_text = "요청을 받았습니다. 현재는 고정된 메시지로 응답합니다."
        # -----------------------------------

        # Google Chat에 보낼 응답 형식 (JSON)
        response = {'text': response_text}
        print(f"Sending response: {response}")
        return jsonify(response)

    # 스페이스에 봇이 추가/삭제된 이벤트 처리
    elif event_type == 'ADDED_TO_SPACE' or event_type == 'REMOVED_FROM_SPACE':
        print(f"Event type: {event_type}")
        # 이 이벤트 유형에는 별도 응답 본문이 필요 없을 수 있습니다.
        return jsonify({})

    # 그 외 처리하지 않는 이벤트 유형
    else:
        print(f"Ignoring event type: {event_type}")
        return jsonify({})

# --- 3. 웹 요청 처리 라우트 ---
# Google Chat이 POST 요청을 보낼 엔드포인트('/')를 정의합니다.
@app.route('/', methods=['POST'])
def handle_post_request():
    """HTTP POST 요청을 처리하고 챗봇 로직 함수를 호출합니다."""
    print("--- POST request received ---")
    try:
        # 요청 본문(body)에서 JSON 데이터 파싱
        event_data = request.get_json()

        # 데이터가 없거나 JSON 형식이 아니면 오류 반환
        if not event_data:
            print("Error: No data received or not JSON")
            return jsonify({'error': 'No data received or not JSON'}), 400 # Bad Request

        # 핵심 로직 함수 호출 및 결과 반환
        return handle_chat_event_logic(event_data)

    except Exception as e:
        # 로직 처리 중 예상치 못한 오류 발생 시 처리
        print(f"Error handling POST request: {e}")
        traceback.print_exc() # 콘솔에 상세 오류 스택 출력
        # Google Chat에는 일반적인 오류 메시지 반환 (HTTP 500)
        return jsonify({'error': 'An internal error occurred while processing the event.'}), 500 # Internal Server Error

# --- 4. 서버 실행 (메인 블록) ---
# 이 스크립트가 직접 실행될 때 (예: python main.py) Flask 개발 서버를 시작합니다.
if __name__ == "__main__":
    print("--- Script running in __main__ block ---")
    try:
        # Cloud Run 환경에서는 PORT 환경 변수로 포트 번호가 주어집니다.
        # 로컬 테스트 시에는 기본값 8080을 사용합니다.
        port = int(os.environ.get("PORT", 8080))

        print(f"--- Starting Flask development server on host 0.0.0.0, port {port} ---")
        # host='0.0.0.0'은 컨테이너 외부(Cloud Run 환경) 또는 로컬 네트워크에서 접근 가능하게 합니다.
        # debug=False 또는 생략: 운영 환경 권장 설정
        app.run(host='0.0.0.0', port=port)

    except Exception as e:
        print(f"--- ERROR: Failed to start Flask server: {e} ---")
        traceback.print_exc()
