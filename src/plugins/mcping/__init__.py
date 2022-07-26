import random
import asyncio
import re
import time
import os
import threading

from nonebot import Config, Env, on_message, require, get_bot, logger, get_driver
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import permission
from nonebot.permission import Permission
from nonebot.permission import SUPERUSER

from .statusping import pingmc

mc_ping = on_message(
    rule=to_me() & keyword('mcping'),
    priority=15,
    block=True,
    permission=permission.PRIVATE_FRIEND
)

@mc_ping.handle()
async def mc_ping_handler(bot: Bot, event: PrivateMessageEvent, state: T_State):
    
    command = event.get_plaintext().strip()
    if not command.startswith('mcping'):
        return
    command = command.split(' ')
    mchost = Config.dict()['MC_DEFAULT']
    if len(command) == 2:
        mchost = command[1]
    logger.info('repeater | bot [{}] ready to mc_ping in group [{}]'.format(
        event.self_id, event.group_id))
    await mc_ping.finish(pingmc(mchost))
    