import re


def extract_bvid(url_or_bvid: str) -> str:
    """从各种B站链接或纯BV号中提取 BV 号。"""
    if url_or_bvid.startswith("BV"):
        return url_or_bvid
    match = re.search(r'(BV[a-zA-Z0-9]{10})', url_or_bvid)
    if match:
        return match.group(1)
    raise ValueError("无效的B站链接或BV号")