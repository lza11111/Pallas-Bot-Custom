from nonebot.adapters.onebot.v11 import MessageSegment, Message, permission, GroupMessageEvent
import asyncio
import httpx
import requests

SETU_API = 'https://api.lolicon.app/setu/v2'

async def request_one_setu(tag=None, r18=False):
    response = requests.post(SETU_API, json={
        'r18':r18,
        'tag':tag,
    }).json()
    if response['error'] != '':
        return None
    setu = response['data'][0]
    print(setu)
    image = None
    async with httpx.AsyncClient() as client:
        resp = await client.get(setu['urls']['original'])
        if resp.status_code == 200:
            image = resp.content
    if image is not None :
        return setu['title'] + MessageSegment.image(file=image)
