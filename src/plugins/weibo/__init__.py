
import random
import asyncio
import re
import time
import os
import threading

import nonebot
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

from .lib import weibo_extract, weibo_info_get, weibo_long_text, weibo_image_list, deal_with_weibo

global_config = nonebot.get_driver().config

weibo = on_message(
    priority=14,
    block=False,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)

@weibo.handle()
async def weibo_main(
    bot: Bot, event: GroupMessageEvent, state: T_State
):
    message_str = str(event.get_message())
    
    weibo_id = await weibo_extract(message_str)

    if not weibo_id:
        return
    try:
        weibo_info = await weibo_info_get(weibo_id)
    except TypeError as e:
        await weibo.finish("此微博需要登录查看或者已被删除")

    weibo_message = await deal_with_weibo(weibo_info)
    try:
        await weibo.finish(weibo_message)
    except ActionFailed as e:
        try:
            await weibo.finish("微博消息发送失败，尝试屏蔽链接和图片\n" + str(weibo_message))
        except ActionFailed as e:
            await weibo.finish("微博消息发送失败，以下是纯文本内容\n" + str(weibo_message))
    
        
