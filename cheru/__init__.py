import time
import os
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.log import logger, default_format
from cheru import config


version = '0.1.0'
name = 'cheruBot'
os.makedirs('/log', exist_ok=True)
error_log_file = os.path.expanduser('./log/error.log')


def _format_offset(seconds_offset):
    """
    将偏移秒数转换为UTC±X
    注意：这里没有考虑时区偏移非整小时的，使用请修改处理方式
    :param seconds_offset 偏移秒数
    :return: 格式化后的时区偏移
    """
    hours_offset = int(seconds_offset/60/60)
    if hours_offset >= 0:
        return "UTC+" + str(hours_offset)
    else:
        return "UTC" + str(hours_offset)


def init():
    seconds_offset = time.localtime().tm_gmtoff
    local_utc = _format_offset(seconds_offset)
    if local_utc != 'UTC+8':
        logger.warning('当前时区不是东8区，请修改到正确的时区后再运行本程序')
        os._exit(0)
    kwargs = {
        'superusers': config.SUPERUSERS,
        'nickname': config.NICKNAME,
        'command_start': config.COMMAND_START,
        'command_sep': config.COMMAND_SEP,
        'debug': config.DEBUG
    }
    nonebot.init(**kwargs)
    driver = nonebot.get_driver()
    driver.register_adapter('cqhttp', CQHTTPBot)

    config_ = driver.config
    config_.savedata = 'data/service'

    nonebot.load_builtin_plugins()
    nonebot.load_plugin("nonebot_plugin_apscheduler")
    nonebot.load_plugin('nonebot_plugin_rauthman')
    if config.DEBUG:
        nonebot.load_plugin('nonebot_plugin_docs')
        nonebot.load_plugin('nonebot_plugin_test')
    nonebot.load_plugins('cheru/plugin')

    logger.add(error_log_file, rotation='0:00',
               format=default_format, compression='zip', enqueue=True, backtrace=True, diagnose=True, level='ERROR')
