from flask import Flask, request, jsonify
from flask_cors import CORS
from check_service import CheckService

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",  # 添加 IP 地址版本
            "http://xiaobaobei-checker-vue:5173",  # 添加 Vue 容器
            "http://srv415056.hstgr.cloud:5173"    # 添加实际域名
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

check_service = CheckService()  # 创建service实例


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()

    # 调用service处理数据
    result = check_service.process_data(data)

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
