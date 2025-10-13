import requests
import random



def randomSeed() -> int:
    num = random.randint(100000, 1999999)
    return num

def getJinmanImageUrlBySeed(num: int) -> tuple[str, str]:
    url = f"https://cdn-msp3.jm18c-tyu.net/media/albums/{num}.jpg"
    return url, f"神秘数字：{str(num)}"

def getJinmanImageUrlRand() -> tuple[str, str]:
    return getJinmanImageUrlBySeed(randomSeed())
