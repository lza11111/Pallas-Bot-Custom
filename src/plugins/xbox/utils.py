from db.mongo import group_member_mongo

def query_member_qq_id(group_id: int, xuid: str) -> str:
    result = group_member_mongo.aggregate([
        {'$match': {
            'group_id': group_id,
            'xuid': xuid
        }},
    ])
    return result["user_id"]