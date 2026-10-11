import os
from bilibili_api import Credential

credential = Credential(
  sessdata=os.getenv("BILI_SESSDATA", ""),
  bili_jct=os.getenv("BILI_JCT", "")
)
