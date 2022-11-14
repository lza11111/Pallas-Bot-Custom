import re
import httpx
from bilireq.utils import post

async def b23_extract(text: str):
    if "b23.tv" not in text:
        return None
    if not (b23 := re.compile(r"b23.tv[\\/]+(\w+)").search(text)):
        return None
    try:
        url = f"https://b23.tv/{b23[1]}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True)
        return str(resp.url)
    except TypeError:
        return None

async def get_b23_url(burl: str) -> str:
    """
    b23 链接转换
    Args:
        burl: 需要转换的 BiliBili 链接
    """
    url = "https://api.bilibili.com/x/share/click"
    data = {
        "build": 6700300,
        "buvid": 0,
        "oid": burl,
        "platform": "android",
        "share_channel": "COPY",
        "share_id": "public.webview.0.0.pv",
        "share_mode": 3,
    }
    return (await post(url, data=data))["content"]

async def video_info_get(vid_id):
    async with httpx.AsyncClient() as client:
        if vid_id[:2] == "av":
            video_info = await client.get(
                f"https://api.bilibili.com/x/web-interface/view?aid={vid_id[2:]}"
            )
            video_info = video_info.json()
        elif vid_id[:2] == "BV":
            video_info = await client.get(
                f"https://api.bilibili.com/x/web-interface/view?bvid={vid_id}"
            )
            video_info = video_info.json()
        else:
            raise ValueError("视频 ID 格式错误，只可为 av 或 BV")
        return 