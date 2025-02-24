# 使用 Python 3.11 完整版本作为基础镜像
FROM python:3.11

# 設置 Python 不緩衝輸出
ENV PYTHONUNBUFFERED=1

# 只安裝最基本的工具
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 只安裝 requirements.txt 中的依賴
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录下的所有文件复制到容器的工作目录
COPY . /app

# 声明端口
EXPOSE 5000

# 设置启动命令
CMD ["python", "app.py"]