from db.mongo import group_member_mongo

def query_member_qq_id(group_id: int, xuid: str) -> str | None:
    result = group_member_mongo.find({
            'group_id': group_id,
            'xuid': xuid
        })
    if not result or result.count() == 0:
        return None
    return list(result)[0]['user_id']