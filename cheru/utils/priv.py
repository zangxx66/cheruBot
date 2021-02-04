from nonebot.adapters.cqhttp import Event
import cheru
from datetime import datetime


_black_group = {}  # Dict[group_id, expr_time]
_black_user = {}  # Dict[user_id, expr_time]


def set_block_group(group_id, time):
    _black_group[group_id] = datetime.now() + time


def set_block_user(user_id, time):
    if user_id not in cheru.config.SUPERUSERS:
        _black_user[user_id] = datetime.now() + time


def check_block_group(group_id):
    if group_id in _black_group and datetime.now() > _black_group[group_id]:
        del _black_group[group_id]  # 拉黑时间过期
        return False
    return bool(group_id in _black_group)


def check_block_user(user_id):
    if user_id in _black_user and datetime.now() > _black_user[user_id]:
        del _black_user[user_id]  # 拉黑时间过期
        return False
    return bool(user_id in _black_user)


BLACK = -999
DEFAULT = 0
NORMAL = 1
PRIVATE = 10
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999


def get_user_priv(ev: Event):
    uid = ev.user_id
    if uid in cheru.config.SUPERUSERS:
        return SUPERUSER
    if check_block_user(uid):
        return BLACK
    # TODO: White list
    if ev.detail_type == 'group':
        if not ev.anonymous:
            role = ev.sender['role']
            if role == 'member':
                return NORMAL
            elif role == 'admin':
                return ADMIN
            # for cqhttpmirai
            elif role == 'administrator':
                return ADMIN
            elif role == 'owner':
                return OWNER
        return NORMAL
    if ev.detail_type == 'private':
        return PRIVATE
    return NORMAL


def check_priv(ev: Event, require: int) -> bool:
    if ev.detail_type == 'group':
        return bool(get_user_priv(ev) >= require)
    else:
        return False  # 不允许私聊
