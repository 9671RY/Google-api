import os
import json
from flask import Flask, request, jsonify

# Flask 앱 만들기
app = Flask(__name__)

# 이전에 만든 챗봇 로직 함수 (거의 그대로 사용)
def handle_chat_event_logic(event):
    """Google Chat 이벤트 로직 처리"""
    print(f"Received event: {json.dumps(event, indent=2)}") # 로그 기록

    event_type = event.get('type')

    if event_type == 'MESSAGE':
        response_text = "테스트 완료되었습니다. 질문 감사합니다."
        response = {'text': response_text}
        # Flask에서는 jsonify를 사용하거나 직접 json.dumps 결과를 Response 객체로 반환할 수 있습니다.
        # 여기서는 간단히 딕셔너리를 jsonify로 변환하여 반환합니다.
        return jsonify(response)

    elif event_type == 'ADDED_TO_SPACE' or event_type == 'REMOVED_FROM_SPACE':
        print(f"Bot was {event_type}")
        return jsonify({}) # 빈 응답

    else:
        print(f"Ignoring event type: {event_type}")
        return jsonify({}) # 빈 응답

# Google Chat이 POST 요청을 보낼 경로 설정
@app.route('/', methods=['POST'])
def handle_post_request():
    """POST 요청을 받아 챗봇 로직 함수로 넘김"""
    # 요청 본문(body)에서 JSON 데이터 가져오기
    event_data = request.get_json()
    if not event_data:
        return jsonify({'error': 'No data received or not JSON'}), 400

    # 챗봇 로직 함수 호출하고 결과 반환
    return handle_chat_event_logic(event_data)

# 프로그램이 직접 실행될 때 웹 서버 시작
if __name__ == "__main__":
    # Cloud Run이 제공하는 PORT 환경 변수 가져오기 (없으면 기본값 8080)
    port = int(os.environ.get("PORT", 8080))
    # 서버 실행: host='0.0.0.0' 은 컨테이너 외부에서 접근 가능하게 함
    app.run(host='0.0.0.0', port=port)
