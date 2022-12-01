
import random
import asyncio
import re
import time
import os
import threading

from nonebot import on_message, require, get_bot, get_driver
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import permission, MessageSegment
from nonebot.permission import Permission
from nonebot.permission import SUPERUSER
from src.common.config import BotConfig

from .lib import b23_extract, get_b23_url, video_info_get
from .draw import binfo_image_create

bilibli = on_message(
    priority=14,
    block=False,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)

@bilibli.handle()
async def bilibili_main(
    bot: Bot, event: GroupMessageEvent, state: T_State
):
    message_str = str(event.get_message())
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
            await bilibli.finish("视频不存在或解析失败")
        else:
            pass
            # await Interval.manual(int(video_info["data"]["aid"]))
        try:
            logger.info(f"开始生成视频信息图片：{video_info['data']['aid']}")
            b23_url = await get_b23_url(
                f"https://www.bilibili.com/video/{video_info['data']['bvid']}"
            )
            image = await asyncio.to_thread(binfo_image_create, video_info, b23_url)
        except Exception: # noqa
            logger.exception("视频解析 API 调用出错")
            await bilibli.finish("视频解析 API 调用出错")
        await bilibli.finish(MessageSegment.image(file=image) + b23_url)