from typing import Generator, List, Optional, Union, Tuple, Dict, Any
import asyncio
import re
import httpx

import nonebot
from nonebot.log import logger

global_config = nonebot.get_driver().config

async def weibo_extract(text: str):
    if "weibo" not in text:
        return None
    if not (weibo_id := re.compile(r"weibo.(?:cn|com)/\w+/(\d+|\w{9})").search(text)):
        return None
    return weibo_id[1]

async def weibo_info_get(weibo_id):
    url = f"https://weibo.com/ajax/statuses/show?id={weibo_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        try:
            return resp.json()
        except Exception as e:
            logger.error(f"获取微博失败: {weibo_id} {e}")
            return None

async def weibo_long_text(weibo_id) -> Union[str,None]:
    url = f"https://weibo.com/ajax/statuses/longtext?id={weibo_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, cookies={"SUB": global_config.weibo_sub})
        try:
            json = resp.json()
            if 'data' in json:
                return json['data']['longTextContent']
            return None
        except Exception as e:
            logger.error(f"获取长微博失败: {weibo_id} {e}")
            return None

def weibo_image_list(weibo_detail):
    if 'pic_ids' not in weibo_detail or 'pic_infos' not in weibo_detail:
        return []
    pic_ids = weibo_detail['pic_ids']
    pic_urls = []
    for pic_id in pic_ids:
        pic_urls.append(weibo_detail['pic_infos'][pic_id]['large']['url'])
    return pic_urls
