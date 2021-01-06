import nonebot
import cheru
from cheru import config

cheru.init()

if __name__ == "__main__":
    nonebot.run(host=config.HOST, port=config.PORT)
