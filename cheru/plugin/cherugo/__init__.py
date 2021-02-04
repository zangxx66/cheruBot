import re
from itertools import zip_longest
from nonebot.adapters.cqhttp import escape, Bot, Event, MessageSegment
from nonebot.permission import MESSAGE
from nonebot import MatcherGroup
from nonebot_plugin_rauthman import isInService


sv = MatcherGroup(type='message', rule=isInService('cherugo', 1))

CHERU_SET = '切卟叮咧哔唎啪啰啵嘭噜噼巴拉蹦铃'
CHERU_DIC = {c: i for i, c in enumerate(CHERU_SET)}
ENCODING = 'gb18030'
rex_split = re.compile(r'\b', re.U)
rex_word = re.compile(r'^\w+$', re.U)
rex_cheru_word: re.Pattern = re.compile(rf'切[{CHERU_SET}]+', re.U)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def word2cheru(w: str) -> str:
    c = ['切']
    for b in w.encode(ENCODING):
        c.append(CHERU_SET[b & 0xf])
        c.append(CHERU_SET[(b >> 4) & 0xf])
    return ''.join(c)


def cheru2word(c: str) -> str:
    if not c[0] == '切' or len(c) < 2:
        return c
    b = []
    for b1, b2 in grouper(c[1:], 2, '切'):
        x = CHERU_DIC.get(b2, 0)
        x = x << 4 | CHERU_DIC.get(b1, 0)
        b.append(x)
    return bytes(b).decode(ENCODING, 'replace')


def str2cheru(s: str) -> str:
    c = []
    for w in rex_split.split(s):
        if rex_word.search(w):
            w = word2cheru(w)
        c.append(w)
    return ''.join(c)


def cheru2str(c: str) -> str:
    return rex_cheru_word.sub(lambda w: cheru2word(w.group()), c)


sv_txt_to_cheru = sv.on_startswith(
    msg='切噜一下', permission=MESSAGE, block=True)


@sv_txt_to_cheru.handle()
async def cherulize(bot: Bot, event: Event, state: dict):
    msg = str(event.message).strip()
    msg = msg.replace(msg[:4], '').strip()
    if not msg:
        await sv_txt_to_cheru.finish()
    if len(msg) > 500:
        await sv_txt_to_cheru.finish('切、切噜太长切不动勒切噜噜...')
    state['cheru'] = msg


@sv_txt_to_cheru.got('cheru')
async def cherulize_cheru(bot: Bot, event: Event, state: dict):
    msg = state['cheru']
    txt = str2cheru(msg)
    res = f'切噜～♪{txt}'
    await sv_txt_to_cheru.finish(res)


sv_cheru_to_txt = sv.on_startswith(
    msg='切噜～♪', permission=MESSAGE, block=True)


@sv_cheru_to_txt.handle()
async def decherulize(bot: Bot, event: Event, state: dict):
    msg = str(event.message).strip()
    msg = msg.replace(msg[:4], '').strip()
    if not msg:
        await sv_cheru_to_txt.finish()
    if len(msg) > 1501:
        await sv_cheru_to_txt.finish('切、切噜太长切不动勒切噜噜...')
    state['cheru'] = msg


@sv_cheru_to_txt.got('cheru')
async def decherulize_cheru(bot: Bot, event: Event, state: dict):
    msg = state['cheru']
    uid = event.user_id
    at = MessageSegment.at(uid)
    res = escape(cheru2str(msg))
    result = f'{at}的切噜噜是：\n{res}'
    await sv_cheru_to_txt.finish(result)
