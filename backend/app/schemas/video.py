from pydantic import BaseModel


class ParseRequest(BaseModel):
    url: str  # 用户粘贴的B站链接或BV号