from cheru import aiorequests
from cheru.utils import helper
import nonebot
from nonebot import MatcherGroup
from nonebot.log import logger
from nonebot.permission import MESSAGE
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot_plugin_rauthman import isInService
from urllib.parse import quote
# from pixivpy3 import AppPixivAPI
from pixivpy3 import ByPassSniApi
from .config import *
import random
import datetime


sv = MatcherGroup(type='message', rule=isInService('pixiv', 1))
# aapi = AppPixivAPI()
aapi = ByPassSniApi()
aapi.require_appapi_hosts(hostname="public-api.secure.pixiv.net")
aapi.set_accept_language('jp')
sv_search = sv.on_startswith(
    msg='/pixiv', permission=MESSAGE, block=True)


@sv_search.handle()
async def pixiv_handle(bot: Bot, event: Event, state: dict):
    msg = str(event.message).strip()
    msg = msg.replace('/pixiv', '')
    if not msg:
        logger.info('pixiv_handle | no keyword')
        await sv_search.finish()
    state['keyword'] = msg


@sv_search.got('keyword')
async def pixiv_got(bot: Bot, event: Event, state: dict):
    keyword = state['keyword']
    if helper.is_number(keyword) is True:
        pid = int(keyword)
        result = await get_image(pid)
    else:
        key = quote(keyword)
        result = await pixiv_search(key)
    if result is None:
        await sv_search.finish('request failed')
    else:
        await sv_search.finish(result)


async def pixiv_search(keyword):
    if not keyword:
        return
    url = f'https://www.pixiv.net/ajax/search/artworks/{keyword}?word={keyword}&order=date_d&mode=all&p=1&s_mode=s_tag&type=all&lang=ja'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'referer': f'https://www.pixiv.net/tags/{keyword}/artworks?s_mode=s_tag'
    }
    try:
        resp = await aiorequests.get(url, headers=headers, timeout=20)
        res = await resp.json()
    except Exception as e:
        logger.error(e)
        return None
    error = res['error']
    if error is True:
        logger.error(f'pixiv | pixiv_search| {res}')
        return None
    body = res['body']
    popular = body['popular']
    permanent = popular['permanent']
    if not len(permanent):
        return 'no hot result'
    artwork = random.choice(permanent)
    pid = artwork['id']
    title = artwork['title']
    userName = artwork['userName']
    link = f'https://www.pixiv.net/artworks/{pid}'
    image = await get_image(pid)
    result = f'''
{title}
画师：{userName}
{image}
{link}
'''.strip()
    return result


async def get_image(pid):
    url = 'https://api.pixiv.cat/v1/generate'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    payload = {'p': pid}
    try:
        resp = await aiorequests.post(url, headers=headers, json=payload, timeout=20)
        res = await resp.json()
    except Exception as e:
        return None
    success = res['success']
    if success is False:
        return res['error']
    multiple = res['multiple']
    msg = ''
    if multiple:
        img_url = res['original_urls_proxy']
        for item in img_url:
            image = MessageSegment.image(item)
            msg += f'{image}\n'
        msg = msg.strip()
    else:
        img_url = res['original_url_proxy']
        msg = MessageSegment.image(img_url)
    return msg


sv_rank = sv.on_command(cmd='pixiv_rank', aliases={
                        '/p站排行榜'}, permission=MESSAGE, block=True)


@sv_rank.handle()
async def pixiv_rank(bot: Bot, event: Event, state: dict):
    # uid = bot.config.superusers[0]
    # sid = bot.self_id

    now = datetime.datetime.now()
    last = datetime.timedelta(days=1)
    lastday = now - last
    yesterday = lastday.strftime('%Y-%m-%d')
    try:
        aapi.login(USERNAME, PWD)
        res = aapi.illust_ranking(mode='day', date=yesterday)
    except Exception as e:
        await sv_rank.finish('exception')
        return
    if 'has_error' in res:
        error_info = res['errors']['system']['message']
        res_info = f'pixivrank error:{error_info}'
        await sv_rank.finish(res_info)
        return
    if not res.illusts:
        logger.info('no pixiv rank result')
        await sv_rank.finish('no result')
        return
    works = res.illusts[:5]
    rank_list = ''
    for item in works:
        pid = item['id']
        title = item['title']
        account = item['user']['name']
        image = await get_image(pid)
        link = f'https://www.pixiv.net/artworks/{pid}'
        rank_list += f'>>>{title}\n画师：{account}\n{image}\n{link}\n'
    msg = f'======pixiv排行榜======\n{rank_list}'.strip()
    await sv_rank.finish(msg)
