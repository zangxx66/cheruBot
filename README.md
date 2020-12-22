# cheruBot  

A QQ bot for プリコネR  

## 简介  

**cheruBot:** 基于 [nonebot2](https://github.com/nonebot/nonebot2) 框架的QQ机器人，正在将自己魔改的Bot从nonebot迁移至nonebot2中  

## 目录

``` 
├─cheru
│  ├─log  :日志目录
│  ├─plugin  :插件根目录
│  │  ├─arena
│  │  │  
│  │  ├─botmanager
│  │  │  
│  │  ├─cherugo
│  │  │  
│  │  ├─pixiv
│  │  │ 
│  │  └─schedule
│  │      
│  └─utils  :工具集
├─res  :静态资源目录
│  ├─font  :字体
│  ├─img  :图片
│  │  └─priconne
│  │      ├─gadget
│  │      ├─stamp
│  │      └─unit
│  └─record  :声音
└─tests  
```

## 功能  

cheruBot 以公主连结国服为主，为玩家提供各种方便的服务：
 
**日程表推送**  
**pixiv查询**  
~~**公会战管理**~~  
**切噜语翻译**  
**jjc挖矿查询**  
~~**官方动态推送**~~  
~~**官方四格漫画推送**~~  
~~**抽卡模拟**~~  
**jjc作业查询**  
**jjc背刺提醒**  

## 安装部署    

1. 安装python3.8  
2. 安装poetry [文档](https://python-poetry.org/docs/#installation)  
3. 克隆本仓库  
``` 
git clone https://github.com/zangxx66/cheruBot  
```  
4. 安装依赖  
``` 
poetry install  
```  
5. 运行  
``` 
poetry run python3.8 run.py  
```  

## 使用方法  

### 竞技场  

**将你的作业网key填入cheru/plugin/arena/config.py文件中**  

|指令|说明|
|-----|-----|
|(b\|日\|台)怎么拆+防守阵容|jjc作业查询|
|刷新作业+防守阵容|刷新缓存|
|挖矿+排名|查询余矿|
|查询jjc错误码(错误码)|查询作业网返回的错误码|  

### 切噜语翻译  

|指令|说明|
|-----|-----|
|切噜一下+需加密的文本||

## 感谢  
[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)  
[yobot](https://yobot.win/)  
[pcrbot](https://github.com/pcrbot)  
[干炸里脊资源站](https://redive.estertion.win/)  
[公主连结Re: Dive Fan Club - 硬核的竞技场数据分析站](https://pcrdfans.com/)  
以及各种插件的作者