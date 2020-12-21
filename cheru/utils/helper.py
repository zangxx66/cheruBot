from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt
import base64
import unicodedata
import zhconv
import asyncio
from nonebot.adapters.cqhttp import Bot, MessageSegment, Message
from nonebot.log import logger


def pic2b64(pic: Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def fig2b64(plt: plt) -> str:
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def concat_pic(pics, border=5):
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border),
                    (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des


def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string


def is_number(s):
    '''判断是否是数字'''
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


async def broadcast(bot: Bot, msg, sv_name, interval_time=0.5, randomiser=None):
    self_id = bot.self_id
    if isinstance(msg, (str, MessageSegment, Message)):
        msg = (msg, )
    group_list = await bot.get_group_list(self_id=self_id)
    for group in group_list:
        try:
            gid = group['group_id']
            for message in msg:
                await asyncio.sleep(interval_time)
                message = randomiser(message) if randomiser else message
                await bot.send_group_msg(group_id=gid, message=message, auto_escape=False)
            l = len(message)
            if l:
                logger.info(f'{sv_name} | 群{gid}投递{l}条消息成功')
        except Exception as e:
            logger.info(f'{sv_name} | 群{gid}投递消息失败')
