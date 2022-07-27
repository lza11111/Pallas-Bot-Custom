from email import message
import requests
import json

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

global_config = nonebot.get_driver().config

sipcheck = on_message(
    rule=to_me() & keyword('sipcheck'),
    priority=15,
    block=True,
    permission=permission.PRIVATE
)

@sipcheck.handle()
async def sipcheck_handler(bot: Bot, event: PrivateMessageEvent, state: T_State):
    command = event.get_plaintext().strip()
    if not command.startswith('sipcheck'):
        return
    command = command.split(' ')
    msg = ''
    if len(command) == 2:
        certNo = command[1]
    else:
        msg = '请输入证件号码'
        await sipcheck.finish(msg)
    req = requests.post('https://ent.sipprh.com/ModuleDefaultCompany/RentManage/SearchRentNo', data={'CertNo': certNo}).text
    if req:
        rel_list = json.loads(req)
        msg = certNo[-4:] + ' ' + rel_list['currentDate'] + ' ' + rel_list['prompWord']
    else:
        msg = '查询失败'
    logger.info('repeater | bot [{}] ready to check sip info'.format(
        event.self_id))
    await sipcheck.finish(msg)

if __name__ == "__main__":
    pass
