"""这是配置文件
"""

# 机器人端口
PORT = 9222
# 监听地址，不建议使用0.0.0.0，如有开放web需求请使用端口转发
HOST = '127.0.0.1'
# HOST='172.17.0.1' # linux+docker用这个
# 配置超级用户
SUPERUSERS = [849694269]
# 配置机器人昵称
NICKNAME = ['xcw']
# 配置命令起始字符
COMMAND_START = {''}
# 配置命令分割字符
COMMAND_SEP = set()

# Debug模式，不知道是什么请关闭
DEBUG = True

# 发送图片/语音协议
# 可选'base64，http，file'
# 建议使用file形式，base64发送大图有可能失败
# 使用http协议请自行配置RES_URL指向RES_DIR
RES_PROTOCOL = 'file'
RES_DIR = r'./res/'
RES_URL = 'http://127.0.0.1:8080/static/'

PUBLIC_BASE_URL = ''
