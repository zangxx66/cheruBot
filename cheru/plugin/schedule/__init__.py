from urllib import request
from .constant import *
import json
import datetime
import re
import os
import aiofiles
from nonebot import MatcherGroup, require, get_bots
from nonebot.permission import GROUP
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from cheru.utils import helper


URL = 'https://static.biligame.com/pcr/gw/calendar.js'
header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
current_path = os.path.abspath(__file__)
absPath = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
config_file = f'{absPath}/config.json'

# data = {
#     'calendar_days': 7,  # 日程表返回包括今天在内多长时间的日程，默认是7天
#     'Refresh_date': '',  # 上次爬取日程表的日期
#     'schedule_data': ''  # 从官方日历爬取下来的数据
# }

# day_key里保存的是每天的信息分类，"qdhd"是多倍掉落庆典，"tdz"是公会战，
# "tbhd"是公会之家家具上架，"jqhd"是活动地图，"jssr"是角色生日
# 你可以自定义这个列表，删掉不想看到的活动
day_key = ["qdhd", "tdz", "tbhd", "jqhd"]


sv = MatcherGroup(type='message')
sv_query = sv.on_command(cmd='schedule', aliases={'国服日程表', '日程表'}, permission=GROUP, block=True)


@sv_query.handle()
async def Schedule(bot: Bot, ev: Event, state: dict):
    # 调用的时候比对上次爬取日程表时间，不是今天就重新爬取日程表，是今天就直接返回
    p = config_file
    await checkFolder(p)
    data = await readJson(p)
    if data == FAILURE:
        data = {
            'calendar_days': 7,
            'Refresh_date': '',
            'schedule_data': ''
        }
        await writeJson(p, data)

    if data['Refresh_date'] != str(datetime.date.today()):
        status = await refresh_schedule()
        if not status[0]:
            await sv_query.finish(f'刷新日程表失败，错误代码{status[1]}')
            return
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
        await writeJson(p, data)
        result = await return_schedule()
        await sv_query.finish(result)
    else:
        result = await return_schedule()
        await sv_query.finish(result)


sv_refresh = sv.on_command(cmd='schedule_refresh', aliases={'刷新日程表'}, permission=GROUP, block=True)


@sv_refresh.handle()
async def re_Schedule(bot: Bot, ev: Event, state: dict):
    status = await refresh_schedule()
    if status[0]:
        await sv_refresh.finish('刷新日程表成功')
        p = config_file
        await checkFolder(p)
        data = await readJson(p)
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
        await writeJson(p, data)
    else:
        await sv_refresh.finish(f'刷新日程表失败，错误代码{status[1]}')


sv_today = sv.on_command(cmd='schedule_today', aliases={'今日活动', '日程', '今日日程'}, permission=GROUP, block=True)


@sv_today.handle()
async def Schedule_today(bot: Bot, ev: Event, state: dict):
    p = config_file
    await checkFolder(p)
    data = await readJson(p)
    if data['Refresh_date'] != str(datetime.date.today()):
        status = await refresh_schedule()
        if not status[0]:
            await sv_today.finish(f'刷新日程表失败，错误代码{status[1]}')
            return
        data['Refresh_date'] = str(datetime.date.today())  # 爬取时间改为今天
        await writeJson(p, data)
        result = await return_schedule(1)
        await sv_today.finish(result)
    else:
        result = await return_schedule(1)
        await sv_today.finish(result)


async def refresh_schedule():
    # 刷新日程表
    schedule = request.Request(URL)
    schedule.add_header('User-Agent', header)
    p = config_file
    await checkFolder(p)
    data = await readJson(p)
    with request.urlopen(schedule, timeout=20) as f:
        if f.code != 200:  # 检查返回的状态码是否是200
            return [False, f.code]

        rew_data = f.read().decode('utf-8')  # bytes类型转utf-8

        rew_data = rew_data[152:-36]
        # 有的时候官方数据最后会多一个逗号导致json.load失败，这里处理一下
        _bool = 1
        while _bool:
            if rew_data[-_bool] == '"':
                _bool = 0
                break
            if rew_data[-_bool] == ',':
                rew_data = rew_data[:-_bool] + rew_data[-(_bool-1):]
            _bool += 1
        data['schedule_data'] = json.loads(rew_data)  # 保存到'schedule_data'
        await writeJson(p, data)
        return [True, "ok"]


async def return_schedule(calendar_days=7):
    # 返回日程表信息

    t = datetime.datetime.today().date()  # 要读取的日期
    year, month, day = str(t).split("-")  # 分割年月日
    if int(day) < 10:
        day = day[1]

    activity_info_list = []
    info_list = []
    infos = ''

    p = config_file
    await checkFolder(p)
    data = await readJson(p)

    for _ in range(calendar_days):
        for i in data['schedule_data']:
            if i['year'] == year and i['month'] == month:  # 官方数据每一个月份是一个列表，检查当前列表年月是否符合
                if day in i['day']:  # 检查是否有查询日期当天的数据
                    for key in day_key:
                        if i['day'][day][key] != '':  # 空的活动数据跳过

                            info_list.extend(re.findall(
                                "class='cl-t'>.+?</div>", i['day'][day][key]))  # 用正则截取活动信息

                if info_list:  # 如果列表不是空的
                    # 去掉每条信息前后的正则匹配参数，只保留活动信息
                    activity_info_list = [info[13:-6] for info in info_list]

                if not activity_info_list:  # 如果列表是空的
                    activity_info_list[0] = '没有活动信息'

                infos += '=======' + \
                    str(t).replace("-", "年", 1).replace("-",
                                                        "月", 1) + '日' + '=======\n'
                for i in activity_info_list:
                    infos += '>>>' + i + '\n'

        t += datetime.timedelta(days=1)  # 改为下一天的日期
        year, month, day = str(t).split("-")  # 分割年月日
        if int(day) < 10:
            day = day[1]

        activity_info_list = []
        info_list = []

    # 返回活动信息字符串
    return infos


async def checkFolder(path):
    dirPath = path[:path.rfind('/')]
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


async def readJson(p):
    if not os.path.exists(p):
        return FAILURE
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = json.loads(content)
    return content


async def writeJson(p, info):
    async with aiofiles.open(p, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(info))
    return SUCCESS


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', hour='8', minute='0')
async def send_schedule():
    status = await refresh_schedule()
    if get_bots():
        bot = list(get_bots().values())[0]
    else:
        logger.warning('未连接任何ws对象')
        return
    if not status[0]:
        self_id = bot.self_id
        uid = bot.config.superuser[0]
        await bot.send_private_msg(self_id=self_id, user_id=uid, message=f'更新日程表发生错误：{status[1]}')
        return
    p = config_file
    await checkFolder(p)
    data = await readJson(p)
    data['Refresh_date'] = str(datetime.date.today())
    await writeJson(p, data)
    result = await return_schedule(1)
    await helper.broadcast(bot, result, '日程表', 2)
