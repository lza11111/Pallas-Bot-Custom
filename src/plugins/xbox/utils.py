from typing import Union
from db.mongo import group_member_mongo

class GroupMemberStatus:
    group_id: int
    xuid: str
    user_id: int
    last_presence_text: str

def query_member(group_id: int, xuid: str) -> Union[GroupMemberStatus,None]:
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

def update_member(group_id: int, xuid: str, user_id: int, last_presence_text: str):
    group_member_mongo.update_one({
        'group_id': group_id,
        'xuid': xuid,
        'user_id': user_id,
    }, {
        '$set': {
            'last_presence_text': last_presence_text
        }
    }, upsert=True)