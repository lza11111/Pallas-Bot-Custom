import database
import models

import json
import pypinyin


def text_to_pinyin(text: str):
    return ''.join([item[0] for item in pypinyin.pinyin(
        text, style=pypinyin.NORMAL, errors='ignore')]).lower()


# return [cq_result: str, is_plain_text: bool, msg_text: str, msg_pinyin: str]
def mirai2cq(msg: str):
    seg = json.loads(msg)
    is_plain_text = True
    res = ''
    msg_text = ''
    for item in seg:
        if item['type'] == 'Plain':
            res += item['text']
            msg_text += item['text']
        elif item['type'] == 'At':
            is_plain_text = False
            target = item['target']
            res += '[CQ:at,qq={}]'.format(target)
        elif item['type'] == 'Image':
            is_plain_text = False
            imageId = item['imageId'].replace(
                '{', '').replace('}', '').replace('-', '')
            imageId = imageId.split('.')[0]
            imageId = imageId.lower()
            res += '[CQ:image,file={}.image,subType=1]'.format(imageId)
        elif item['type'] == 'File':
            is_plain_text = False
        elif item['type'] == 'Quote':
            is_plain_text = False
        elif item['type'] == 'Face':
            is_plain_text = False
        else:
            is_plain_text = False
            print('type error', item['type'])

    return res, is_plain_text, msg_text, text_to_pinyin(msg_text)


def migrate_message():
    all_msg = models.MsgRecord.select()

    data = []
    for item in all_msg:
        if item.group_id == 716692626:  # 测试群
            continue
        raw_msg, is_pt, pt, pinyin = mirai2cq(item.msg)
        # print(raw_msg, is_pt, pt, pinyin)
        if raw_msg:
            data.append(
                {'group': item.group_id,
                 'user': item.user_id,
                 'raw_msg': raw_msg,
                 'is_plain_text': is_pt,
                 'text_msg': pt,
                 'pinyin_msg': pinyin,
                 'time': item.time}
            )
    num = 30000
    for i in range(0, len(data), num):
        database.Message.insert_many(data[i:i+num]).execute()


def migrate_context():
    all_msg = models.ReplyRecord.select()

    data = []
    for item in all_msg:
        if item.group_id == 716692626:  # 测试群
            continue
        raw_msg, is_pt, pt, pinyin = mirai2cq(item.pre_msg)
        rep_raw_msg, _1, _2, _3 = mirai2cq(item.reply_msg)

        if raw_msg and rep_raw_msg:
            data.append({
                'group': item.group_id,
                'above_raw_msg': raw_msg,
                'above_is_plain_text': is_pt,
                'above_text_msg': pt,
                'above_pinyin_msg': pinyin,
                'below_raw_msg': rep_raw_msg,
                'count': item.count,
                'latest_time': 0})
    num = 30000
    for i in range(0, len(data), num):
        database.Context.insert_many(data[i:i+num]).on_conflict('replace').execute()


if __name__ == '__main__':
    models.AmiyaDataBase.create_base()
    database.DataBase.create_base()

    migrate_message()
    migrate_context()