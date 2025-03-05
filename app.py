from flask import Flask, request, jsonify
from flask_cors import CORS

from ai_process import AIProcess
from ai_service import AIService

# from kenlm_service import KenlmService

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",  # 添加 IP 地址版本
            "http://xiaobaobei-checker-vue:5173",  # 添加 Vue 容器
            "http://srv415056.hstgr.cloud:5173"  # 添加实际域名
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    article = data.get('article', '')
    if not article:
        return {
            "status": "error",
            "message": "文章内容不能为空",
            "errors": []
        }

    model = data.get('model', 'none')
    if model != 'KenLM':
        ai_service = AIService()
        ai_process = AIProcess()
        message = ''
        if model.lower().startswith('claude'):
            bot = model
            message = ai_service.claude_service(data, bot)
        elif model.lower().startswith('poe'):
            bot = model[4:]
            message = ai_service.poe_service(data, bot)
            print(message)
        result = ai_process.process_data(article, message)
    else:
        result = {
            "status": "error",
            "message": "模型選擇錯誤",
            "errors": []
        }
        # kenlm_service = KenlmService()
        # result = kenlm_service.process_data(data)

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
