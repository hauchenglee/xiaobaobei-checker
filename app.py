from flask import Flask, request, jsonify
from check_service import CheckService

app = Flask(__name__)
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
    app.run()
