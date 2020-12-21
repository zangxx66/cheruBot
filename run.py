import os
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.log import logger, default_format
from cheru import config

kwargs = {
    'superusers': config.SUPERUSERS,
    'nickname': config.NICKNAME,
    'command_start': config.COMMAND_START,
    'command_sep': config.COMMAND_SEP,
    'debug': config.DEBUG
}
nonebot.init(**kwargs)
app = nonebot.get_app()
driver = nonebot.get_driver()
driver.register_adapter('cqhttp', CQHTTPBot)
nonebot.load_builtin_plugins()
nonebot.load_plugin("nonebot_plugin_apscheduler")
if config.DEBUG:
    nonebot.load_plugin('nonebot_plugin_docs')
    nonebot.load_plugin('nonebot_plugin_test')
nonebot.load_plugins('cheru/plugin')

os.makedirs('cheru/log', exist_ok=True)
error_log_file = os.path.expanduser('./cheru/log/error.log')
logger.add(error_log_file, rotation='0:00',
           format=default_format, compression='zip', enqueue=True, backtrace=True, diagnose=True, level='ERROR')


if __name__ == "__main__":
    nonebot.run(host=config.HOST, port=config.PORT)
