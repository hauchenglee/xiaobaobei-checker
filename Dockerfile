# 使用 Python 3.11 完整版本作为基础镜像
FROM python:3.11

# 安装基础工具和调试工具
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    net-tools \
    dnsutils \
    vim \
    htop \
    telnet \
    procps \
    lsof \
    netcat-openbsd \
    tcpdump \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 包和开发工具
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython \
    httpie

# 将当前目录下的所有文件复制到容器的工作目录
COPY . /app

# 声明端口
EXPOSE 5000

# 设置启动命令
CMD ["python", "app.py"]