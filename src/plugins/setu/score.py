
from db.mongo import message_mongo, context_mongo, blacklist_mongo, score_mongo

def query_score(user_id, group_id, score_type='setu_score'):
    msg_sum = message_mongo.count_documents({
        '_id': user_id,
    })

    score_used = score_mongo.find_one(
        {'user_id': user_id, 'group_id': group_id})
    return msg_sum - score_used[score_type]


def use_score(user_id, group_id, score_type, score):
    score_mongo.find_one_and_update(
        filter={'user_id': user_id, 'group_id': group_id},
        update={'$inc': {score_type: score}},
        upsert=True
    )
    return 0


if __name__ == "__main__":
    use_score(1, 1, 'setu_score', 10)
    query_score(1, 1)
    pass
