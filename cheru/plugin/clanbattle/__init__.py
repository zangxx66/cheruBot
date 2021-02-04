from nonebot import MatcherGroup
from nonebot.adapters.cqhttp import Bot, Event
from nonebot_plugin_rauthman import isInService
from nonebot.permission import MESSAGE
from nonebot.log import logger
from nonebot.plugin import on_message

from cheru.utils import res, helper
from cheru import config
from typing import (Any, Callable, Dict, Iterable, List, NamedTuple, Optional,
                    Set, Tuple, Union)

from .argparse import ArgParser
from .exception import *


sv = MatcherGroup(type='message', rule=isInService('clanbattle'))
SORRY = 'ごめんなさい！嘤嘤嘤(〒︿〒)'
_registry: Dict[str, Tuple[Callable, ArgParser]] = {}


async def _clanbattle_bus(bot: Bot, event: Event, state: dict):
    # check prefix
    start = ''
    for m in event.message:
        if m.type == 'text':
            start = m.data.get('text', '').lstrip()
            break
    # if not start or start[0] not in '!！':
    #     return

    # find cmd
    plain_text = event.message.extract_plain_text()
    cmd, *args = plain_text[0:].split()
    cmd = helper.normalize_str(cmd)
    if cmd in _registry:
        func, parser = _registry[cmd]
        try:
            logger.info(
                f'Message {event.message_id} is a clanbattle command, start to process by {func.__name__}.')
            args = parser.parse(args, event.message)
            await func(bot, event, args)
            logger.info(
                f'Message {event.message_id} is a clanbattle command, handled by {func.__name__}.')
        except DatabaseError as e:
            await bot.send(event, f'DatabaseError: {e.message}\n{SORRY}\n※请及时联系维护组', at_sender=True)
        except ClanBattleError as e:
            await bot.send(event, e.message, at_sender=True)
        except Exception as e:
            logger.exception(e)
            logger.error(
                f'{type(e)} occured when {func.__name__} handling message {event.message_id}.')
            await bot.send(event, f'Error: 机器人出现未预料的错误\n{SORRY}\n※请及时联系维护组', at_sender=True)

sv_message = on_message(permission=MESSAGE, block=False,
                        handlers=[_clanbattle_bus])


def cb_cmd(name, parser: ArgParser) -> Callable:
    if isinstance(name, str):
        name = (name, )
    if not isinstance(name, Iterable):
        raise ValueError('`name` of cb_cmd must be `str` or `Iterable[str]`')
    names = map(lambda x: helper.normalize_str(x), name)

    def deco(func) -> Callable:
        for n in names:
            if n in _registry:
                logger.warning(
                    f'出现重名命令：{func.__name__} 与 {_registry[n].__name__}命令名冲突')
            else:
                _registry[n] = (func, parser)
        return func
    return deco


from .cmdv2 import *


sv_msg = sv.on_command(cmd='battle_help', aliases={
                       '手册'}, permission=MESSAGE, block=True)


@sv_msg.handle()
async def battle_help(bot: Bot, event: Event, state: dict):
    base_url = config.PUBLIC_BASE_URL
    url = f'{base_url}/guide/manual.html'
    await sv_msg.finish(url)
