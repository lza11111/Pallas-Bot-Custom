import random
import asyncio
import re
import time
import os
import threading

import nonebot
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

global_config = nonebot.get_driver().config

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
    mchost = global_config.mc_default
    if len(command) == 2:
        mchost = command[1]
    logger.info('repeater | bot [{}] ready to mc_ping'.format(
        event.self_id))
    await mc_ping.finish(pingmc(mchost))
    