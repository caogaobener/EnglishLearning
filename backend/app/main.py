from __future__ import annotations

import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# 任务的唯一状态
TaskStatus = Literal["uploaded", "processing", "transcribing", "completed", "failed"]

# 限制文件大小时长以及种类
MAX_FILE_SIZE = 500 * 1024 * 1024
MAX_DURATION_SECONDS = 2 * 60 * 60
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov"}

# 任务状态字典，存储每个上传任务的状态和结果
tasks: dict[str, dict[str, str | None]] = {}

app = FastAPI(title="English Learning Upload API")
# 跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 不同任务状态更新函数
def update_task(task_id: str, status: TaskStatus, **values: str | None) -> None:
    tasks[task_id] = {**tasks[task_id], "status": status, **values}

# 终端命令执行函数，用于调用 FFmpeg 处理音频
def run_command(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            # 命令失效抛出calledProcessError异常
            check=True,
            # 捕获命令输出
            capture_output=True,
            # 只把输出作为文本返回，而不是字节
            text=True,
            timeout=timeout,
        )
    # 统一异常处理，前端只需要捕获 RuntimeError 即可
    except FileNotFoundError as exc:
        raise RuntimeError("服务器未安装 FFmpeg，请先安装 ffmpeg 和 ffprobe") from exc
    # 命令失效
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr.strip() or "FFmpeg 处理失败") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("媒体处理超时") from exc

# 读取媒体时长
def get_duration(input_path: Path) -> float:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_path),
        ],
        timeout=30,
    )
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError("无法读取媒体时长") from exc


def transcribe(audio_path: Path) -> str:
    # 不在初版绑定 Whisper 或云端服务，避免引入重量级依赖和密钥配置。
    raise RuntimeError(
        "转写服务尚未配置。当前已完成文件上传和 FFmpeg 音频提取流程。"
    )

# 处理上传文件的函数，提取音频并进行转写
def process_upload(task_id: str, source_path: Path, work_dir: Path) -> None:
    try:
        update_task(task_id, "processing")
        duration = get_duration(source_path)
        if duration > MAX_DURATION_SECONDS:
            raise RuntimeError("媒体时长不能超过 2 小时")

        audio_path = work_dir / "audio.wav"
        run_command(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(source_path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                str(audio_path),
            ],
            timeout=15 * 60,
        )

        update_task(task_id, "transcribing")
        text = transcribe(audio_path)
        update_task(task_id, "completed", text=text)
    except Exception as exc:
        update_task(task_id, "failed", error=str(exc))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

# 保存上传的文件
async def save_upload(upload: UploadFile, destination: Path) -> int:
    size = 0
    with destination.open("wb") as output:
        # 传一点数据就写入文件然后判断大小
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                # 文件过大，删除以前存的部分内存文件并抛出异常
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="文件不能超过 500MB")
            output.write(chunk)
    return size

# 文件上传接口
# 202 Accepted 表示请求已接受处理，但尚未完成
@app.post("/api/uploads", status_code=202)
async def create_upload(
    # 后台处理任务
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict[str, str]:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="仅支持 mp3、wav、m4a、mp4、mov 文件")
    # 生成唯一任务 ID （随机数）
    task_id = uuid.uuid4().hex
    # 创建临时任务id文件夹
    # prefix这个是定义了文件夹的前缀，mkdtemp是创建一个临时文件夹的函数
    work_dir = Path(tempfile.mkdtemp(prefix=f"english-learning-{task_id}-"))
    # 创建临时文件路径（在对应的临时文件夹中），保存上传的文件
    source_path = work_dir / f"source{extension}"
    tasks[task_id] = {
        "status": "uploaded",
        "filename": file.filename,
        "text": None,
        "error": None,
    }

    try:
        await save_upload(file, source_path)
    except Exception:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise

    background_tasks.add_task(process_upload, task_id, source_path, work_dir)
    return {"task_id": task_id, "status": "uploaded"}

# 查询上传任务状态接口
@app.get("/api/uploads/{task_id}")
async def get_upload_status(task_id: str) -> dict[str, str | None]:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="上传任务不存在或已过期")
    return task
