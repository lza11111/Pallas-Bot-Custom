import random
import asyncio
import re
import time
import os
import threading

import nonebot
from nonebot import on_message, on_startswith
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageSegment, Message
from nonebot.adapters.onebot.v11 import permission
from nonebot.permission import Permission
from nonebot.permission import SUPERUSER

from .setu import request_one_setu
from .score import query_score, use_score

request_setu = on_startswith(
    msg='我要色色',
    rule=to_me(),
    priority=13,
    block=True,
    permission=permission.GROUP
)

@request_setu.handle()
async def request_setu_handler(bot: Bot, event: GroupMessageEvent, state: T_State):
    score = query_score(event.user_id, event.group_id)
    if score < 100:
        await request_setu.finish(Message(f'[CQ:reply,id={event.message_id}]不可以色色！'))
    try:
        await request_setu.send(Message(f'[CQ:reply,id={event.message_id}]{str(await request_one_setu())}'))
        use_score(event.user_id, event.group_id, 'setu_score', 100)
    except Exception as e:
        logger.exception(e)
        await request_setu.finish(Message(f'[CQ:reply,id={event.message_id}]色色失败！不消耗点数 {e}'))


score_query = on_message(
    rule=to_me() & keyword('可以色色吗'),
    priority=14,
    block=True,
    permission=permission.GROUP
)

@score_query.handle()
async def score_query_handler(bot: Bot, event: GroupMessageEvent, state: T_State):
    score = query_score(event.user_id, event.group_id)
    msg = f'你的色色点数还剩{score}'
    if score > 100:
        msg += '，可以色色'
    else:
        msg += '，不可以色色了哦'
    await score_query.finish(msg)

rule_query = on_message(
    rule=to_me() & keyword('来点色图'),
    priority=14,
    block=True,
    permission=permission.GROUP
)

@rule_query.handle()
async def rule_query_handler(bot: Bot, event: GroupMessageEvent, state: T_State):
    await rule_query.finish('请@我并说 我要色色, 每次色色会消耗100点色色点数哦')
                            