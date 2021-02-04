from . import sv
from .spider import *
import nonebot
from nonebot import require
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.permission import MESSAGE
from nonebot_plugin_rauthman import isInService
from cheru.utils import helper


async def news_poller(bot: Bot, spider: BaseSpider, TAG):
    if not spider.item_cache:
        await spider.get_update()
        logger.info(f'{TAG}新闻缓存为空，已加载至最新')
        return
    news = await spider.get_update()
    if not news:
        logger.info(f'未检索到{TAG}新闻更新')
        return
    logger.info(f'检索到{len(news)}条{TAG}新闻更新！')
    await helper.broadcast(bot, spider.format_items(news), TAG, interval_time=0.5)


async def send_news(bot: Bot, ev: Event, spider: BaseSpider, sv: Matcher, max_num=5):
    if not spider.item_cache:
        await spider.get_update()
    news = spider.item_cache
    news = news[:min(max_num, len(news))]
    msg = spider.format_items(news)
    await sv.finish(msg)


sv_news = sv.on_command(cmd='blnews', aliases={
                        'B服新闻', 'b服新闻', 'B服日程', 'b服日程'}, permission=MESSAGE, block=True, rule=isInService('B服新闻', 1))


@sv_news.handle()
async def blnews(bot: Bot, event: Event, state: dict):
    await send_news(bot, event, SonetSpider, sv_news)


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', minute='*/5')
async def news_scheduler():
    if nonebot.get_bots():
        bot = list(nonebot.get_bots().values())[0]
    else:
        logger.warning('未连接任何ws对象')
        return
    await news_poller(bot, BiliSpider, 'B服新闻')
