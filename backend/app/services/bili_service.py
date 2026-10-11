import asyncio
import httpx
from bilibili_api import video

from app.core.config import credential

# 内存任务字典（下一轮会替换成数据库）
tasks = {}


async def process_bili_task(task_id: str, bvid: str):
    """后台任务：解析B站字幕。"""
    tasks[task_id] = {"status": "processing", "text": None, "error": None}

    try:
        v = video.Video(bvid, credential=credential)
        info = await v.get_info()
        cid = info["cid"]

        subtitle_info = await v.get_subtitle(cid)
        subtitles = subtitle_info.get("subtitles", [])

        if not subtitles:
            print(f"⚠️ 视频 {bvid} 没有CC字幕，正在降级调 ASR...")
            await asyncio.sleep(3)
            raise RuntimeError("该视频没有CC字幕，需要降级处理（ASR逻辑待接入）")

        subtitle_url = subtitles[0]["subtitle_url"]
        if not subtitle_url.startswith("http"):
            subtitle_url = "https:" + subtitle_url

        async with httpx.AsyncClient() as client:
            response = await client.get(subtitle_url)
            subtitle_data = response.json()

        result = []
        for item in subtitle_data.get("body", []):
            result.append({
                "start": item["from"],
                "end": item["to"],
                "text": item["content"]
            })

        tasks[task_id] = {
            "status": "completed",
            "text": result,
            "title": info["title"],
            "error": None
        }

    except Exception as exc:
        tasks[task_id] = {"status": "failed", "text": None, "error": str(exc)}