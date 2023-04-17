
from io import BytesIO
import asyncio

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

from .draw import create_weibo_image
from .lib import weibo_extract, weibo_info_get, deal_with_weibo

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
        logger.exception(f"此微博需要登录查看或者已被删除 {e}")
        await weibo.finish("此微博需要登录查看或者已被删除")

    try:
        weibo_message = await deal_with_weibo(weibo_info)
        await weibo.finish(weibo_message)
    except ActionFailed as e:
        try:
            image, urls = await create_weibo_image(weibo_info)
            image_bytes = BytesIO()
            image.save(image_bytes, 'JPEG')
            await weibo.finish(MessageSegment.image(file=image_bytes) + '\n'.join(urls))
        except ActionFailed as e:
            logger.exception(f"操作失败，内容被风控 {e}")
            await weibo.finish("操作失败，内容被风控")
        except TypeError as e:
            logger.exception(f"微博解析失败 {e}")
            await weibo.finish("微博解析失败")
    
        
