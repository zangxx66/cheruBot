from .config import AUTH_KEY
from cheru.utils import data_source, chara
from cheru import aiorequests
from nonebot.log import logger
import base64
import os
import time
from collections import defaultdict
try:
    import ujson as json
except:
    import json


sql = data_source.sqlite('arena', 'arena', ['attack', 'defend'])
quick_key_dic = {}
_last_query_time = 0

DB_PATH = os.path.expanduser('~/.cheru/arena_db.json')
DB = {}
try:
    with open(DB_PATH, encoding='utf8') as f:
        DB = json.load(f)
    for k in DB:
        DB[k] = {
            'like': set(DB[k].get('like', set())),
            'dislike': set(DB[k].get('dislike', set()))
        }
except FileNotFoundError:
    logger.warning('arena_db.json not found, will create when needed.')


def dump_db():
    j = {}
    for k in DB:
        j[k] = {
            'like': list(DB[k].get('like', set())),
            'dislike': list(DB[k].get('dislike', set()))
        }
    with open(DB_PATH, 'w', encoding='utf8') as f:
        json.dump(j, f, ensure_ascii=False)


def get_likes(id_):
    return DB.get(id_, {}).get('like', set())


def add_like(id_, uid):
    e = DB.get(id_, {})
    f = e.get('like', set())
    k = e.get('dislike', set())
    f.add(uid)
    k.discard(uid)
    e['like'] = f
    e['dislike'] = k
    DB[id_] = e


def get_dislikes(id_):
    return DB.get(id_, {}).get('dislike', set())


def add_dislike(id_, uid):
    e = DB.get(id_, {})
    f = e.get('like', set())
    k = e.get('dislike', set())
    f.discard(uid)
    k.add(uid)
    e['like'] = f
    e['dislike'] = k
    DB[id_] = e


def refresh_quick_key_dic():
    global _last_query_time
    now = time.time()
    if now - _last_query_time > 300:
        quick_key_dic.clear()
    _last_query_time = now


def __get_auth_key():
    return AUTH_KEY


def get_true_id(quick_key: str, user_id: int) -> str:
    mask = user_id & 0xffffff
    if not isinstance(quick_key, str) or len(quick_key) != 5:
        return None
    qkey = (quick_key + '===').encode()
    qkey = int.from_bytes(base64.b32decode(
        qkey, casefold=True, map01=b'I'), 'little')
    qkey ^= mask
    return quick_key_dic.get(qkey, None)


def gen_quick_key(true_id: str, user_id: int) -> str:
    qkey = int(true_id[-6:], 16)
    while qkey in quick_key_dic and quick_key_dic[qkey] != true_id:
        qkey = (qkey + 1) & 0xffffff
    quick_key_dic[qkey] = true_id
    mask = user_id & 0xffffff
    qkey ^= mask
    return base64.b32encode(qkey.to_bytes(3, 'little')).decode()[:5]


async def query(id_list, user_id, region=1, force=False):
    id_list = [x * 100 + 1 for x in id_list]
    t = id_list.copy()
    t.sort()
    attack = ",".join(str(v) for v in t)
    result_list = sql.select('arena', 'attack', attack)
    if len(result_list) == 0 or force:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'authorization': __get_auth_key()
        }
        payload = {'_sign': 'a', 'def': id_list, 'nonce': 'a',
                   'page': 1, 'sort': 1, 'ts': int(time.time()), 'region': region}
        try:
            resp = await aiorequests.post('https://api.pcrdfans.com/x/v1/search', headers=header, json=payload, timeout=10)
            res = await resp.json()
        except Exception as e:
            logger.error(e)
            return 'Arena query failed.'
        if res['code']:
            code = int(res['code'])
            return f'Arena query failed.\nCode={code}'
        result_list = res['data']['result']
        if not result_list:
            return []
        result = ','.join(str(v) for v in result_list)
        sql.insertOrUpdate('arena', ['attack', 'defend'], (attack, result))
        logger.info('arena | 在线查询')
    else:
        try:
            result_list = str(result_list[0])
            result_list = eval(result_list)
            result_list = eval(result_list[0])
            logger.info('arena | 本地缓存')
        except Exception as e:
            logger.error(e)
            return 'Arena query failed.'
    ret = []
    index = 0
    try:
        for entry in result_list:
            eid = entry['id']
            likes = get_likes(eid)
            dislikes = get_dislikes(eid)
            ret.append({
                'qkey': gen_quick_key(eid, user_id),
                'atk': [chara.fromid(c['id'] // 100, c['star'], c['equip']) for c in entry['atk']],
                'up': entry['up'],
                'down': entry['down'],
                'my_up': len(likes),
                'my_down': len(dislikes),
                'user_like': 1 if user_id in likes else -1 if user_id in dislikes else 0
            })
            index += 1
        return ret
    except Exception as e:
        logger.error(e)
        return 'Arena query failed.'


async def do_like(qkey, user_id, action):
    true_id = get_true_id(qkey, user_id)
    if true_id is None:
        raise KeyError
    add_like(true_id, user_id) if action > 0 else add_dislike(true_id, user_id)
    dump_db()


ERROR_CODE = {
    0: 'Success',
    1: 'User is not login',
    2: 'Success but find nothing',
    3: 'Duplicated Battle',
    4: 'Duplicated Battle but updated info',
    5: 'Not enough e Lements',
    100: 'System Error',
    101: 'Database find data error',
    102: 'Unknown Parameters',
    103: 'Signature not valid',
    104: 'CORS not valid',
    105: 'Server Error',
    106: 'User exist',
    107: 'User not exist',
    108: 'Password not match',
    109: 'DupLicated data',
    110: 'Game unit not found',
    111: 'No Pernission',
    112: ' Third party request error',
    113: 'Data is processing',
    114: 'Skill not found',
    115: 'Expired request',
    116: 'Contains sensitive word',
    117: 'Over 1imit',
    118: 'Pending request',
    129: 'Router not found',
    600: ' Unsupported region',
    601: 'IP blocked',
    429: 'Too many requests',
}
