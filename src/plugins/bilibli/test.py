
import asyncio
import re
import traceback
from .lib import b23_extract, get_b23_url, video_info_get
from .draw import binfo_image_create

async def test():
    message_str = "testtesthttps://www.bilibili.com/video/BV1Z54y1L7ZLetssa"
    if "b23.tv" in message_str:
        message_str = await b23_extract(message_str) or message_str
    p = re.compile(r"av(\d{1,15})|BV(1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2})")
    video_number = p.search(message_str)
    if video_number:
        video_number = video_number[0]
    video_info = await video_info_get(video_number) if video_number else None
    if video_info:
        if video_info["code"] != 0:
            # await Interval.manual(member.id)
            print("视频不存在或解析失败")
        else:
            pass
            # await Interval.manual(int(video_info["data"]["aid"]))
        try:
            print(f"开始生成视频信息图片：{video_info['data']['aid']}")
            b23_url = await get_b23_url(
                f"https://www.bilibili.com/video/{video_info['data']['bvid']}"
            )
            image = await asyncio.to_thread(binfo_image_create, video_info, b23_url)
            print(f"生成视频信息图片成功：{video_info['data']['aid']}")
            with open('test.png', 'wb') as f:
                f.write(image)
        except Exception as e: # noqa
            print("视频解析 API 调用出错")
            traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(test())