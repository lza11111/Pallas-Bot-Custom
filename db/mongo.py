import pymongo

import nonebot
from nonebot.adapters import Event

global_config = nonebot.get_driver().config

mongo_client = pymongo.MongoClient(global_config.mongodb_connection, 27017)

mongo_db = mongo_client['PallasBot']

message_mongo = mongo_db['message']
message_mongo.create_index(name='time_index',
                           keys=[('time', pymongo.DESCENDING)])

context_mongo = mongo_db['context']
context_mongo.create_index(name='keywords_index',
                           keys=[('keywords', pymongo.HASHED)])
context_mongo.create_index(name='count_index',
                           keys=[('count', pymongo.DESCENDING)])
context_mongo.create_index(name='time_index',
                           keys=[('time', pymongo.DESCENDING)])
context_mongo.create_index(name='answers_index',
                           keys=[("answers.group_id", pymongo.TEXT),
                                 ("answers.keywords", pymongo.TEXT)],
                           default_language='none')

score_mongo = mongo_db['score']
score_mongo.create_index(name='user_id_index',
                         keys=[('user_id', pymongo.HASHED)])

blacklist_mongo = mongo_db['blacklist']
blacklist_mongo.create_index(name='group_index',
                             keys=[('group_id', pymongo.HASHED)])

group_member_mongo = mongo_db['group_member']
group_member_mongo.create_index(name='group_index',
                                    keys=[('group_id', pymongo.HASHED)])
group_member_mongo.create_index(name='xuid_index',
                                    keys=[('xuid', pymongo.HASHED)])
                                    
__all__ = ['mongo_client', 'message_mongo', 'context_mongo', 'score_mongo', 'blacklist_mongo']