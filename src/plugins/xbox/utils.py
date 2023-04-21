from typing import Union
from db.mongo import group_member_mongo

def query_member(group_id: int, xuid: str) -> Union[dict, None]:
    result = group_member_mongo.find({
            'group_id': group_id,
            'xuid': xuid
        })
    if not result or result.count() == 0:
        return None
    return list(result)[0]

def query_member_list(group_id: int) -> list:
    result = group_member_mongo.find({
            'group_id': group_id
        })
    if not result or result.count() == 0:
        return []
    return list(result)

def update_member(group_id: int, xuid: str, user_id: int, last_presence_text: str, last_push_time: Union[int,None] = None):
    set_value: dict[str, Union[str,int]] = {
        'last_presence_text': last_presence_text,
    }
    if last_push_time is not None:
        set_value['last_push_time'] = last_push_time
    group_member_mongo.update_one({
        'group_id': group_id,
        'xuid': xuid,
        'user_id': user_id,
    }, {
        '$set': set_value
    }, upsert=True)