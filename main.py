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
    """POST 요청을 받아 챗봇 로직 함수로 넘김"""
    try:
        # 요청 본문(body)에서 JSON 데이터 가져오기
        event_data = request.get_json()
        if not event_data:
            print("Error: No data received or not JSON") # 오류 로그 추가
            # 400 Bad Request 반환
            return jsonify({'error': 'No data received or not JSON'}), 400

        # 챗봇 로직 함수 호출하고 결과 반환
        return handle_chat_event_logic(event_data)

    except Exception as e:
        # 예상치 못한 오류 발생 시 로그 기록 및 오류 응답 반환
        print(f"Error handling POST request: {e}")
        traceback.print_exc() # 콘솔에 상세 오류 스택 출력
        # 500 Internal Server Error 반환
        return jsonify({'error': 'An internal error occurred'}), 500

# --- 메인 실행 블록 ---
if __name__ == "__main__":
    # Cloud Run이 제공하는 PORT 환경 변수 가져오기 (없으면 기본값 8080)
    port = int(os.environ.get("PORT", 8080))
    print(f"--- Starting Flask App on host 0.0.0.0 port {port} ---") # 시작 로그 추가
    # 서버 실행: host='0.0.0.0' 은 컨테이너 외부에서 접근 가능하게 함
    # debug=True는 개발 중에 유용하지만, 운영 환경에서는 False로 설정하거나 제거하는 것이 좋습니다.
    app.run(host='0.0.0.0', port=port) # debug=True 제거 권장
