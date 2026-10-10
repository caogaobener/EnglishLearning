import asyncio
from bilibili_api import video, Credential
import requests

credential = Credential(
    sessdata="36a32716%2C1807082886%2Cea5b6%2Aa2CjDDkewGSGfT0VUZ4DjVT21Q2JpI9tuSHH9ouLCZgQqpxcY-OyVtsYmGARNImy99Sl4SVkhVUC01dWVGSHduUE5SUHZqWHRBazRxY3M1OFVIUF9RVWQ2N00tcTU3NUp6YjVsMFNVSDVMWjRCQTA0Mlp2UHB2UV9teXVtbGhCU3JDdzREZDJQVFhnIIEC",
    bili_jct="ac6514d1076a6db4f4dbb02e9c412fcb"
)

async def get_video_subtitle(bvid: str):
    print(f"正在解析视频: {bvid}")
    v = video.Video(bvid=bvid, credential=credential)
    
    # 1. 获取视频基本信息
    try:
        info = await v.get_info()
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return []
        
    cid = info["cid"]
    print(f"✅ 视频 CID: {cid}")
    print(f"✅ 视频标题: {info['title']}")
    
    # 2. 获取字幕列表
    subtitle_info = await v.get_subtitle(cid)#字幕的总体信息，包括字幕的下载链接等信息
    subtitles = subtitle_info.get("subtitles", [])#字幕列表，每种语言的字幕信息
    if not subtitles:
        print("❌ 该视频没有 CC 字幕！")
        return []
    
    print(f"✅ 发现 {len(subtitles)} 种字幕，正在下载...")
    
    # 3. 获取字幕下载链接
    subtitle_url = subtitles[0]["subtitle_url"]
    if not subtitle_url.startswith("http"):
        subtitle_url = "https:" + subtitle_url
    
    # 4. 下载并解析
    response = requests.get(subtitle_url)
    subtitle_data = response.json()
    
    result = []
    for item in subtitle_data.get("body", []):
        result.append({
            "start": item["from"],
            "end": item["to"],
            "text": item["content"]
        })
    
    return result

if __name__ == "__main__":
    # 找一个你确定有CC字幕的英语视频BV号，替换掉这里的
    # 例如：这是TED官方在B站的一个视频，通常有字幕
    bvid = "BV1G3411w7LL" 
    subtitles = asyncio.run(get_video_subtitle(bvid))
    
    if subtitles:
        print("\n🎉 转写成功！前5条字幕如下：")
        for sub in subtitles[:5]:
            print(f"[{sub['start']:.2f} - {sub['end']:.2f}] {sub['text']}")