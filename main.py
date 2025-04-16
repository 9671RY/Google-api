import os
import json
import traceback # 오류 상세 출력을 위해 추가
from flask import Flask, request, jsonify

# Flask 앱 만들기
app = Flask(__name__)

# --- 로직 함수 정의가 먼저 와야 합니다 ---
def handle_chat_event_logic(event):
    """Google Chat 이벤트 로직 처리"""
    # 로그 기록 (보안을 위해 실제 운영에서는 민감 정보 필터링 필요)
    print(f"Received event: {json.dumps(event, indent=2)}")

    event_type = event.get('type')

    if event_type == 'MESSAGE':
        # --- 여기가 챗봇의 응답을 결정하는 부분 ---
        # 지금은 항상 같은 메시지를 보내지만, 나중에 Vertex AI 로직을 넣을 수 있습니다.
        response_text = "테스트 완료되었습니다. 질문 감사합니다."
        # ---------------------------------------
        response = {'text': response_text}
        return jsonify(response)

    elif event_type == 'ADDED_TO_SPACE' or event_type == 'REMOVED_FROM_SPACE':
        print(f"Bot was {event_type}")
        return jsonify({}) # 빈 응답

    else:
        print(f"Ignoring event type: {event_type}")
        return jsonify({}) # 빈 응답

# --- 로직 함수 정의 후에 라우트 정의 ---
@app.route('/', methods=['POST'])
def handle_post_request():
    print("--- POST request received at '/' endpoint! ---")
    # 요청 처리 로직 없이 그냥 성공 응답만 반환
    return jsonify({'status': 'POST request received successfully'}), 200

# --- 메인 실행 블록 ---
if __name__ == "__main__":
    # Cloud Run이 제공하는 PORT 환경 변수 가져오기 (없으면 기본값 8080)
    port = int(os.environ.get("PORT", 8080))
    print(f"--- Starting Flask App on host 0.0.0.0 port {port} ---") # 시작 로그 추가
    # 서버 실행: host='0.0.0.0' 은 컨테이너 외부에서 접근 가능하게 함
    # debug=True는 개발 중에 유용하지만, 운영 환경에서는 False로 설정하거나 제거하는 것이 좋습니다.
    app.run(host='0.0.0.0', port=port) # debug=True 제거 권장
