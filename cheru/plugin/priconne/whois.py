from . import sv
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.permission import GROUP, GROUP_ADMIN
from nonebot.exception import FinishedException, NetworkError
from cheru.utils import helper, res, chara
import re


sv_whois = sv.on_regex(r'^((谁是|誰是)(.*)|(.*)(是谁|是誰))', permission=GROUP, block=True)
lmt = helper.FreqLimiter(5)


@sv_whois.handle()
async def whois(bot: Bot, event: Event, state: dict):
    uid = event.user_id
    if not lmt.check(uid):
        msg = f'{MessageSegment.at(uid)}兰德索尔花名册冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)'
        await sv_whois.finish(msg)
    lmt.start_cd(uid)
    name = event.plain_text.strip()
    name_ = name.replace('谁是', '').replace('誰是', '').replace('是谁', '').replace('是誰', '')
    if not name_:
        await sv_whois.finish()
    id_ = chara.name2id(name_)
    confi = 100
    if id == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name_)
    c = chara.fromid(id_)

    msg = ''
    if confi < 100:
        lmt.start_cd(uid, 120)
        msg = f'兰德索尔似乎没有叫"{name_}"的人...'
        await sv_whois.finish(msg)
        msg = f'\n您有{confi}%的可能在找{guess_name}'
    if confi > 60:
        msg += f'{c.icon.cqcode} {c.name}'
        await sv_whois.finish(msg)


sv_reload = sv.on_command(cmd='reload_juese', aliases={
                          '重载角色花名册'}, permission=GROUP_ADMIN, block=True)


@sv_reload.handle()
async def reload_juese(bot: Bot, event: Event, state: dict):
    try:
        chara.update()
        await sv_reload.finish('我好了')
    except (FinishedException, NetworkError) as e:
        logger.error(e)
        await sv_reload.finish()
