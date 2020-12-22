from .data_source import *
from nonebot import MatcherGroup
from nonebot.log import logger
from nonebot.permission import GROUP, PRIVATE
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from cheru.utils import chara, helper, res
import re
import time
import os
from collections import defaultdict
from PIL import Image, ImageSequence, ImageDraw, ImageFont


font_path = res.get('font/seguiemj.ttf').path

aliases = {'怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打',
           '怎麼拆', '怎麼解', '怎麼打', 'jjc查询', 'jjc查詢'}
aliases_b = {'b' + a for a in aliases}
aliases_b1 = {'B' + a for a in aliases}
aliases_b.update(aliases_b1)
aliases_tw = {'台' + a for a in aliases}
aliases_jp = {'日' + a for a in aliases}


sv = MatcherGroup(type='message')
sv_all = sv.on_command(cmd='arena_all', aliases=aliases, permission=GROUP, block=True)


@sv_all.handle()
async def arena_all(bot: Bot, event: Event, state: dict):
    res = await _arena_query(bot, event, 1)
    await sv_all.finish(res)


sv_bl = sv.on_command(cmd='arena_bl', aliases=aliases_b, permission=GROUP, block=True)


@sv_bl.handle()
async def arena_bl(bot: Bot, event: Event, state: dict):
    res = await _arena_query(bot, event, 2)
    await sv_bl.finish(res)


sv_jp = sv.on_command(cmd='arena_jp', aliases=aliases_jp, permission=GROUP, block=True)


@sv_jp.handle()
async def arena_jp(bot: Bot, event: Event, state: dict):
    res = await _arena_query(bot, event, 3)
    await sv_jp.finish(res)


sv_tw = sv.on_command(cmd='arena_tw', aliases=aliases_tw, permission=GROUP, block=True)


@sv_tw.handle()
async def arena_tw(bot: Bot, event: Event, state: dict):
    res = await _arena_query(bot, event, 4)
    await sv_tw.finish(res)


def optimize_pic(img: Image):
    im = Image.new('RGB', img.size, '#ffffff')
    im.paste(img, None, img)
    w, h = im.size
    im.thumbnail((w / 0.9, h / 0.9), Image.ANTIALIAS)
    return im


async def _arena_query(bot: Bot, event: Event, region: int, refresh=False):
    refresh_quick_key_dic()
    uid = event.user_id
    isAt = True if event.detail_type == 'group' else False

    # 处理输入数据
    defen = str(event.message).strip()
    defen = re.sub(r'[?？，,_]', '', defen)
    defen, unknown = chara.roster.parse_team(defen)

    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
        return msg
    if not defen:
        return '查询请发送"怎么拆+防守队伍"，无需+号'
    if len(defen) > 5:
        return '编队不能多于5名角色'
    if len(defen) < 5:
        return '编队不能少于5名角色'
    if len(defen) != len(set(defen)):
        return '编队中含重复角色'
    if any(chara.is_npc(i) for i in defen):
        return '编队中含未实装角色'
    if 1004 in defen:
        return '\n⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称'

    # 执行查询
    # sv.logger.info('Doing query...')
    res = await query(id_list=defen, user_id=uid, region=region, force=refresh)
    # sv.logger.info('Got response!')

    # 处理查询结果
    if isinstance(res, str):
        return f'查询出错，{res}'
    if not len(res):
        return '抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★\n作业上传请前往pcrdfans.com'
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    size = len(res)
    target = Image.new(
        'RGBA', (64*6, 64*size+(size-1)*5), (255, 255, 255, 255))
    draw = ImageDraw.Draw(target)
    ttffont = ImageFont.truetype(font_path, 16)
    index = 0
    for v in res:
        atk = v['atk']
        team_pic = chara.gen_team_pic(atk)
        up = v['up'] + v['my_up']
        down = v['down'] + v['my_down']
        qkey = v['qkey']
        pingjia = f'{qkey}\n\U0001F44D{up}\n\U0001F44E{down}'
        draw.text((64*5, index*(64+5)), pingjia,
                  font=ttffont, fill='#000000')
        target.paste(team_pic, (0, index*(64+5)), team_pic)
        index += 1
    target = optimize_pic(target)
    img = helper.pic2b64(target)
    # 拼接回复
    atk_team = MessageSegment.image(img)
    defen = [chara.fromid(x).name for x in defen]
    defen = f"防守方【{' '.join(defen)}】"
    at = str(MessageSegment.at(uid)) if isAt else event.sender['nickname']

    msg = [
        defen,
        f'已为骑士{at}查询到以下进攻方案：',
        str(atk_team)
    ]

    msg.append('Support by pcrdfans_com')

    return '\n'.join(msg)


sv_errcode = sv.on_command(cmd='arena_err', aliases={'查询jjc错误码'}, permission=GROUP, block=True)


@sv_errcode.handle()
async def arena_err(bot: Bot, event: Event, state: dict):
    msg = str(event.message).strip()
    state['code'] = msg


@sv_errcode.got('code')
async def arena_err_got(bot: Bot, event: Event, state: dict):
    code = state['code']
    res = ''
    if not code:
        for index in ERROR_CODE:
            res = += f'{index}:{ERROR_CODE[index]}\n'
        res = res.strip()
        res = f'''
常见错误码如下：
{res}
'''.strip()
    else:
        msg = int(code)
        res = ERROR_CODE[msg]
    await sv_errcode.finish(res)


sv_refresh = sv.on_command(cmd='arena_refresh', aliases={'刷新作业'}, permission=GROUP, block=True)


@sv_refresh.handle()
async def arena_refresh(bot: Bot, event: Event, state: dict):
    res = await _arena_query(bot, event, 1, True)
    await sv_refresh.finish(res)
