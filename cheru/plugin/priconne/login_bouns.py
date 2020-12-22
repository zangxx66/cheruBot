from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.permission import GROUP
from cheru.utils import helper, res
from . import sv
import random
import os

sv_login = sv.on_command(cmd='login_bonus', aliases={
                         '签到'}, permission=GROUP, block=True)

lmt = helper.DailyNumberLimiter(1)
login_presents = [
    '扫荡券×5',  '卢币×1000', '普通EXP药水×5',  '宝石×50',  '玛那×3000',
    '扫荡券×10', '卢币×1500', '普通EXP药水×15', '宝石×80',  '白金转蛋券×1',
    '扫荡券×15', '卢币×2000', '上级精炼石×3',   '宝石×100', '白金转蛋券×1',
]
todo_list = [
    '找伊绪老师上课',
    '给宫子买布丁',
    '和真琴寻找伤害优衣的人',
    '找镜哥探讨女装',
    '跟吉塔一起登上骑空艇',
    '和霞一起调查伤害优衣的人',
    '和佩可小姐一起吃午饭',
    '找小小甜心玩过家家',
    '帮碧寻找新朋友',
    '去真步真步王国',
    '找镜华补习数学',
    '陪胡桃排练话剧',
    '和初音一起午睡',
    '成为露娜的朋友',
    '帮铃莓打扫咲恋育幼院',
    '和静流小姐一起做巧克力',
    '去伊丽莎白农场给栞小姐送书',
    '观看慈乐之音的演出',
    '解救挂树的队友',
    '来一发十连',
    '井一发当期的限定池',
    '给妈妈买一束康乃馨',
    '购买黄金保值',
    '竞技场背刺',
    '给别的女人打钱',
    '氪一单',
    '努力工作，尽早报答妈妈的养育之恩',
    '成为魔法少女',
    '搓一把日麻'
]


@sv_login.handle()
async def login_bouns(bot: Bot, event: Event, state: dict):
    uid = event.user_id
    if not lmt.check(uid):
        img = res.img('priconne/sign_stamp.jpeg').cqcode
        msg = f'你今天已经盖过章了\n{img}'
        await sv_login.finish(msg)
    lmt.increase(uid)
    folder = res.img('priconne/stamp/').path
    files = os.listdir(folder)
    filename = random.choice(files)
    stamp = res.img('priconne/stamp/', filename)
    present = random.choice(login_presents)
    todo = random.choice(todo_list)
    await sv_login.finish(f'{MessageSegment.at(uid)}\nおかえりなさいませ、主さま\n{stamp.cqcode}\n{present}を獲得しました\n私からのプレゼントです\n主人今天要{todo}吗？')
