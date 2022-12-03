from typing import Generator, List, Optional, Union, Tuple, Dict, Any
import asyncio
import re
import httpx

import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment

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
        pic_urls.append(weibo_detail['pic_infos'][pic_id]['original']['url'])
    return pic_urls

async def deal_with_weibo(weibo_info) -> Union[str, Message, None]:
    if weibo_info and 'error_code' in weibo_info:
        logger.exception(f'微博信息处理出错: {weibo_info}')
        return
    weibo_id = weibo_info['id']
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
                # download image as BytesIO
                async with httpx.AsyncClient() as client:
                    resp = await client.get(image)
                    if resp.status_code == 200:
                        finish += MessageSegment.image(file=resp.content)
            if 'retweeted_status' in weibo_info:
                finish += await deal_with_weibo(weibo_info['retweeted_status']) or MessageSegment.text("\n获取转发微博失败")
            if 'page_info' in weibo_info and 'media_info' in weibo_info['page_info']:
                finish += MessageSegment.text(f"\n视频: {weibo_info['page_info']['media_info']['stream_url_hd']}")
            return finish
        except Exception as e:
            logger.exception(f'微博信息处理出错: {e}')
            return None