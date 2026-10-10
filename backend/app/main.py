import os
import re
import uuid
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bilibili_api import video, Credential

app = FastAPI(title="English Learning B站解析 API")

# 1. 配置跨域（允许前端 5173 端口访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 2. 安全读取 Cookie（优先从环境变量读，读不到就用默认值本地测试）
credential = Credential(
    sessdata="36a32716%2C1807082886%2Cea5b6%2Aa2CjDDkewGSGfT0VUZ4DjVT21Q2JpI9tuSHH9ouLCZgQqpxcY-OyVtsYmGARNImy99Sl4SVkhVUC01dWVGSHduUE5SUHZqWHRBazRxY3M1OFVIUF9RVWQ2N00tcTU3NUp6YjVsMFNVSDVMWjRCQTA0Mlp2UHB2UV9teXVtbGhCU3JDdzREZDJQVFhnIIEC",
    bili_jct="ac6514d1076a6db4f4dbb02e9c412fcb"
)

# 3. 内存任务字典（生产环境建议用 Redis）
tasks = {}

# 4. 定义前端传来的请求体
class ParseRequest(BaseModel):
    url: str  # 用户粘贴的B站链接或BV号

# 5. 工具函数：从各种B站链接中提取 BV 号
def extract_bvid(url_or_bvid: str) -> str:
    if url_or_bvid.startswith("BV"):
        return url_or_bvid
    # 正则匹配BV号（BV后面跟10位字母或数字）
    match = re.search(r'(BV[a-zA-Z0-9]{10})', url_or_bvid)
    if match:
        return match.group(1)#获取第一个匹配的BV号
    raise ValueError("无效的B站链接或BV号")

# 6. 核心后台任务（耗时操作全部在这里，不会阻塞前端请求）
async def process_bili_task(task_id: str, bvid: str):
    # 初始化任务状态为处理中
    tasks[task_id] = {"status": "processing", "text": None, "error": None}
    
    try:
        v = video.Video(bvid, credential=credential)
        info = await v.get_info()
        cid = info["cid"]
        
        # 获取字幕列表
        subtitle_info = await v.get_subtitle(cid)
        subtitles = subtitle_info.get("subtitles", [])
        
        # 🚨 降级策略入口：如果没有CC字幕
        if not subtitles:
            # 模拟耗时操作：实际项目中这里是去下载音频、调ASR API
            # 这里的 await asyncio.sleep(3) 是为了让你测试前端轮询效果
            print(f"⚠️ 视频 {bvid} 没有CC字幕，正在降级调 ASR...")
            await asyncio.sleep(3) 
            raise RuntimeError("该视频没有CC字幕，需要降级处理（ASR逻辑待接入）")
        
        # 提取字幕链接
        subtitle_url = subtitles[0]["subtitle_url"]
        if not subtitle_url.startswith("http"):
            subtitle_url = "https:" + subtitle_url
        
        # 使用 httpx 异步下载字幕（避免阻塞事件循环）
        async with httpx.AsyncClient() as client:
            response = await client.get(subtitle_url)
            subtitle_data = response.json()
        
        # 解析字幕数据
        result = []
        for item in subtitle_data.get("body", []):
            result.append({
                "start": item["from"],
                "end": item["to"],
                "text": item["content"]
            })
        
        # 更新任务状态为完成，存入字幕和标题
        tasks[task_id] = {
            "status": "completed",
            "text": result,
            "title": info['title'],
            "error": None
        }
        
    except Exception as exc:
        # 发生任何错误，更新为失败状态
        tasks[task_id] = {"status": "failed", "text": None, "error": str(exc)}


# 7. 提交解析任务接口（前端发一次）
@app.post("/api/parse", status_code=202)
async def create_parse_task(req: ParseRequest, background_tasks: BackgroundTasks):
    try:
        bvid = extract_bvid(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    task_id = uuid.uuid4().hex
    tasks[task_id] = {"status": "uploaded", "text": None, "error": None}
    
    # 核心：把耗时任务丢给后台，立即给前端返回 task_id
    background_tasks.add_task(process_bili_task, task_id, bvid)
    
    return {"task_id": task_id, "status": "uploaded"}


# 8. 前端轮询查询接口（前端每隔1秒调一次）
@app.get("/api/parse/{task_id}")
async def get_parse_status(task_id: str):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return task

# 9. 方便本地直接 python main.py 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)