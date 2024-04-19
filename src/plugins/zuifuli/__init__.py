
import random
import asyncio
import re
import httpx


from nonebot import on_message, on_command, get_driver
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.adapters.onebot.v11 import permission, MessageSegment
from nonebot.permission import Permission
from nonebot.permission import SUPERUSER
from src.common.config import BotConfig

global_config = get_driver().config

async def jd_extract(text: str):
    if "jd.com" not in text:
        return None
    if not (match := re.compile(r"jd.(?:cn|com)/.*?(\d{5,20}).html").search(text)):
        return None
    return match[1]

zuifuli_extract = on_message(
    priority=14,
    block=False,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER,
)

zuifuli_command = on_command("jd",
    priority=14,
    block=False,
    permission=permission.GROUP_ADMIN | permission.GROUP_OWNER | SUPERUSER,
)

@zuifuli_extract.handle()
async def zuifuli_extract_main(
    bot: Bot, event: GroupMessageEvent, state: T_State
):
    message_str = str(event.get_message())
    sku_id = await jd_extract(message_str)
    if not sku_id:
        return
    result = await zuifuli_main(sku_id)
    await zuifuli_extract.finish(Message(f'[CQ:reply,id={event.message_id}]{str(result)}'))


@zuifuli_command.handle()
async def zuifuli_command_main(
    bot: Bot, event: GroupMessageEvent, state: T_State
):
    message_str = str(event.get_message())
    if not (match := re.compile(r"(\d{5,20})").search(message_str)):
        await zuifuli_extract.finish(Message(f'[CQ:reply,id={event.message_id}]sku_id错误'))
    sku_id = match[1]
    result = await zuifuli_main(sku_id)
    await zuifuli_extract.finish(Message(f'[CQ:reply,id={event.message_id}]{str(result)}'))


async def zuifuli_main(sku_id: str):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(global_config.nodejs_endpoint + f"/zuifuli/compare?skuId={sku_id}")
        try:
            json = resp.json()
            text = ''
            if json["code"] == 200:
                text = f'【{json["data"]["name"]}】\n 最福利价格: {json["data"]["price_z"]}\n 京东价格: {json["data"]["price_jd"]}'
            else:
                raise Exception(json["message"])
            return text
        except Exception as e:
            logger.error(f"接口请求失败: {sku_id} {e}")
            return None
