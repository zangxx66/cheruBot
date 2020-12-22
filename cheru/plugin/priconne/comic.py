from . import sv
import nonebot
from nonebot import require
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.permission import GROUP
import os
import re
import random
import asyncio
from urllib.parse import urljoin, urlparse, parse_qs
try:
    import ujson as json
except:
    import json
from cheru import aiorequests
from cheru.utils import helper, res


def load_index():
    with open(res.get('img/priconne/comic/index.json').path, encoding='utf8') as f:
        return json.load(f)


def get_pic_name(id_):
    pre = 'episode_'
    end = '.png'
    return f'{pre}{id_}{end}'


async def download_img(save_path, link):
    '''
    从link下载图片保存至save_path（目录+文件名）
    会覆盖原有文件，需保证目录存在
    '''
    # sv.logger.info(f'download_img from {link}')
    resp = await aiorequests.get(link, stream=True)
    # sv.logger.info(f'status_code={resp.status_code}')
    if 200 == resp.status_code:
        if re.search(r'image', resp.headers['content-type'], re.I):
            # sv.logger.info(f'is image, saving to {save_path}')
            with open(save_path, 'wb') as f:
                f.write(await resp.content)
                # sv.logger.info('saved!')


async def download_comic(id_):
    '''
    下载指定id的官方四格漫画，同时更新漫画目录index.json
    episode_num可能会小于id
    '''
    base = 'https://comic.priconne-redive.jp/api/detail/'
    save_dir = res.img('priconne/comic/').path
    index = load_index()

    # 先从api获取detail，其中包含图片真正的链接
    # sv.logger.info(f'getting comic {id_} ...')
    url = base + id_
    # sv.logger.info(f'url={url}')
    resp = await aiorequests.get(url)
    # sv.logger.info(f'status_code={resp.status_code}')
    if 200 != resp.status_code:
        return
    data = await resp.json()
    data = data[0]

    episode = data['episode_num']
    title = data['title']
    link = data['cartoon']
    index[episode] = {'title': title, 'link': link}
    # sv.logger.info(f'episode={index[episode]}')

    # 下载图片并保存
    await download_img(os.path.join(save_dir, get_pic_name(episode)), link)

    # 保存官漫目录信息
    with open(os.path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False)
    return id_


sv_search = sv.on_command(cmd='comic_search', aliases={
                          '官漫'}, permission=GROUP, block=True)


@sv_search.handle()
async def comic_handle(bot: Bot, event: Event, state: dict):
    episode = event.plain_text.strip()
    if not re.fullmatch(r'\d{0,3}', episode):
        await sv_search.finish()
    episode = episode.lstrip('0')
    if not episode:
        await sv_search.finish('请输入漫画集数  如：官漫123')
    state['episode'] = episode


@sv_search.got('episode')
async def comic_got(bot: Bot, event: Event, state: dict):
    episode = state['episode']
    index = load_index()
    if episode not in index:
        a = await download_comic(episode)
        index = load_index()
        if a not in index:
            await sv_search.finish(f'未查找到第{episode}话，敬请期待官方更新')
    title = index[episode]['title']
    pic = res.img('priconne/comic/', get_pic_name(episode)).cqcode
    msg = f'プリンセスコネクト！Re:Dive公式4コマ\n第{episode}話 {title}\n{pic}'
    await sv_search.finish(msg)


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', minute='*/5')
async def comic_scheduler():
    if nonebot.get_bots():
        bot = list(nonebot.get_bots().values())[0]
    else:
        logger.warning('未连接任何ws对象')
        return
    index_api = 'https://comic.priconne-redive.jp/api/index'
    index = load_index()

    resp = await aiorequests.get(index_api, timeout=10)
    data = await resp.json()
    id_ = data['latest_cartoon']['id']
    episode = data['latest_cartoon']['episode_num']
    title = data['latest_cartoon']['title']

    if episode in index:
        qs = urlparse(index[episode]['link']).query
        old_id = parse_qs(qs)['id'][0]
        if id_ == old_id:
            logger.info('未检测到官漫更新')
            return

    await download_comic(id_)
    pic = res.img('priconne/comic', get_pic_name(episode)).cqcode
    msg = f'プリンセスコネクト！Re:Dive公式4コマ更新！\n第{episode}話 {title}\n{pic}'
    await helper.broadcast(bot, msg, 'PCR官方四格', 0.5)
