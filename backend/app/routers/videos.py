import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.video import ParseRequest
from app.utils.bili import extract_bvid
from app.services.bili_service import process_bili_task, tasks

router = APIRouter(prefix="/api", tags=["videos"])


@router.post("/parse", status_code=202)
async def create_parse_task(req: ParseRequest, background_tasks: BackgroundTasks):
    try:
        bvid = extract_bvid(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_id = uuid.uuid4().hex
    tasks[task_id] = {"status": "uploaded", "text": None, "error": None}

    background_tasks.add_task(process_bili_task, task_id, bvid)

    return {"task_id": task_id, "status": "uploaded"}


@router.get("/parse/{task_id}")
async def get_parse_status(task_id: str):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return task