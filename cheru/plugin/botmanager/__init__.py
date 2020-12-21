import nonebot
from nonebot import MatcherGroup
from nonebot.permission import PRIVATE, GROUP_ADMIN, GROUP, SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event


sv = MatcherGroup(type='message')
sv_status = sv.on_command(cmd='status', aliases={'/status'}, permission=SUPERUSER, block=True)


@sv_status.handle()
async def handle_get_status(bot: Bot, event: Event, state: dict):
    try:
        sid = bot.self_id
        res = await bot.get_status(self_id=sid)
    except:
        await sv_status.finish('error')
    stat = res['stat']
    packet_received = stat['packet_received']
    packet_sent = stat['packet_sent']
    packet_lost = stat['packet_lost']
    message_received = stat['message_received']
    message_sent = stat['message_sent']
    disconnect_times = stat['disconnect_times']
    lost_times = stat['lost_times']
    info = await bot.call_api('get_login_info')
    nickname = info['nickname']
    msg = f'''
【{nickname}】当前运行状态：
收到的数据包总数：{packet_received}
发送的数据包总数：{packet_sent}
数据包丢失总数：{packet_lost}
接受信息总数：{message_received}
发送信息总数：{message_sent}
TCP链接断开次数：{disconnect_times}
账号掉线次数：{lost_times}
'''.strip()
    await sv_status.finish(msg)


sv_v = sv.on_command(cmd='version', aliases={'V', 'v', 'ver', '查看版本'}, permission=GROUP, block=True)


@sv_v.handle()
async def handle_get_ver(bot: Bot, event: Event, state: dict):
    try:
        res = await bot.get_version_info()
    except:
        await sv_v.finish('error')
    msg = '\n'.join([f'{item}:{res[item]}' for item in res])
    await sv_v.finish(msg)


sv_test = sv.on_command(cmd='zai', aliases={'zai', '在', '在吗'}, permission=SUPERUSER, block=True)


@sv_test.handle()
async def handle_test(bot: Bot, event: Event, state: dict):
    msg = 'はい！私はいつも貴方の側にいますよ！'
    await sv_test.finish(msg)
