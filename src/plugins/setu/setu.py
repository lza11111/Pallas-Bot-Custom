from nonebot.adapters.onebot.v11 import MessageSegment, Message, permission, GroupMessageEvent

import requests

SETU_API = 'https://api.lolicon.app/setu/v2'

def request_one_setu(tag=None, r18=False):
    response = requests.post(SETU_API, json={
        'r18':r18,
        'tag':tag,
    }).json()
    if response['error'] != '':
        return None
    setu = response['data'][0]
    print(setu)
    return MessageSegment.text(
            setu['title']) + MessageSegment.image(file=setu['urls']['original'])

if __name__ == "__main__":
    request_one_setu()
    pass