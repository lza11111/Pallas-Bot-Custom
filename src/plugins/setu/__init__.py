import random
import asyncio
import re
import time
import os
import threading

import nonebot
from nonebot import Config, Env, on_message, on_command
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import permission
from nonebot.permission import Permission
from nonebot.permission import SUPERUSER

from .setu import request_one_setu

MODE = 'private'

def permission_mode(mode):
    if mode == 'group':
        return permission.GROUP
    return permission.PRIVATE

request_setu = on_command(
    cmd='我要色色',
    rule=to_me(),
    priority=15,
    block=True,
    permission=permission_mode(MODE)
)

@request_setu.handle()
async def request_setu_handler(bot: Bot, event: PrivateMessageEvent, state: T_State):
    await request_setu.finish(request_one_setu())

score_query = on_message(
    rule=to_me() & keyword('可以色色吗'),
    priority=15,
    block=True,
    permission=permission_mode(MODE)
)

@score_query.handle()
async def score_query_handler(bot: Bot, event: PrivateMessageEvent, state: T_State):
    
    await score_query.finish()