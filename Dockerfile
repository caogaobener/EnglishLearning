# 1. 使用官方 Python 3.11 的轻量级镜像作为基础
FROM python:3.11-slim

# 2. 设置工作目录为 /app
WORKDIR /app

# 3. 安装 FFmpeg（这是最关键的一步）
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# 4. 把 backend 文件夹里的依赖清单复制到工作目录
COPY backend/requirements.txt .

# 5. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把 backend 文件夹里的所有代码复制到工作目录
COPY backend/ .

# 7. 暴露 8000 端口
EXPOSE 8000

# 8. 启动命令（注意：由于代码在 app 文件夹里，路径是 app.main:app）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]