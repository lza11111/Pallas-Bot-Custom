
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

from .lib import weibo_extract, weibo_info_get, weibo_long_text, weibo_image_list

global_config = nonebot.get_driver().config

weibo = on_message(
    priority=14,
    block=True,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER
)

@weibo.handle()
async def weibo_main(
    bot: Bot, event: GroupMessageEvent, state: T_State
):
    if global_config.blocked_groups and event.group_id in global_config.blocked_groups:
        return
    message_str = event.get_plaintext()
    
    weibo_id = weibo_extract(message_str)

    if not weibo_id:
        return
    weibo_info = await weibo_info_get(weibo_id)
    weibo_text = None
    finish = ''
    if weibo_info:
        logger.info(f'开始处理微博信息: {weibo_id}')
        try:
            if "isLongText" in weibo_info and weibo_info["isLongText"]:
                weibo_text = await weibo_long_text(weibo_id)
            else:
                weibo_text = str(weibo_info['text_raw'])
            
            image_list = weibo_image_list(weibo_info)
            finish = weibo_text or ''
            for image in image_list:
                finish += MessageSegment.image(file=image)
        except Exception as e:
            logger.exception(f'微博信息处理出错: {e}')
            return
        await weibo.finish(finish)