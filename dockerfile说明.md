二、 Dockerfile 的执行逻辑（你只需要理解这一层）
Dockerfile 是从上到下逐行执行的。每一行就是一个命令，像你在终端里敲命令一样。

用你的项目举例：

dockerfile
FROM python:3.11-slim
翻译：先给我一个装了 Python 3.11 的精简版 Linux 系统。
（FROM 永远是第一行，代表“从什么基础开始”）

dockerfile
WORKDIR /app
翻译：在服务器里创建一个 /app 文件夹，后面所有操作都在这个文件夹里进行。
（相当于 cd /app）

dockerfile
RUN apt-get update && apt-get install -y ffmpeg
翻译：用 Linux 的包管理工具，安装 FFmpeg。
（RUN 就是在服务器上执行一条终端命令。这一步是 pip install 做不到的，因为 FFmpeg 不是 Python 库，是系统软件）

dockerfile
COPY backend/requirements.txt .
翻译：把你项目里 backend/requirements.txt 这个文件，复制到服务器的 /app 目录下。
（COPY 就是把你的本地文件搬到服务器里）

dockerfile
RUN pip install --no-cache-dir -r requirements.txt
翻译：在服务器上执行 pip install，照着刚才复制过来的清单，安装 Python 库。

dockerfile
COPY backend/ .
翻译：把你 backend/ 文件夹里的所有代码，全部复制到服务器里。

dockerfile
EXPOSE 8000
翻译：声明“我的应用会跑在 8000 端口”。这只是一个声明，方便平台知道往哪个端口转发流量。

dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
翻译：当容器启动时，执行这行命令来启动你的后端。
（CMD 是 Dockerfile 的最后一行，代表“启动命令”）