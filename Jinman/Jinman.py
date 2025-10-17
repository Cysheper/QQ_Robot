import requests
import random
from DailyProblem import DailyProblem
from GetAndPost import GetAndPost
from ContorlImages import ContorlImages
import json
from playwright.sync_api import sync_playwright
import base64


with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

my_repo = config["GitHub_repo"]
my_token = config["GitHub_Token"]


def randomSeed() -> int:
    num = random.randint(100000, 1999999)
    return num

def getJinmanImageUrlBySeed(num: int) -> tuple[str, str]:
    url = f"https://cdn-msp3.jm18c-tyu.net/media/albums/{num}.jpg"
    return url, f"神秘数字：{str(num)}"

def getJinmanImageUrlRand() -> tuple[str, str]:
    return getJinmanImageUrlBySeed(randomSeed())


def saveImg(url: str, title: str) -> str:

    try:
        print("Shooting Anime Image...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")  # 等待页面加载完成
            png_bytes = page.screenshot(full_page=True)
            browser.close()

        b64 = base64.b64encode(png_bytes).decode("utf-8")

    except Exception as e:
        return "[Error] 拍摄图片错误"
    try:

        filename = title

        path = f"jminfo/{filename}.png"
        # api
        api = f"https://gitee.com/api/v5/repos/Cysheper/my-images/contents/{path}"

        data = {
            "access_token": my_token,
            "message": f"upload {filename}", 
            "content": b64,
            "branch": "master"
        }
        print("Posting Anime Image to Gitee...")
        r = requests.post(api, json=data)
        if r.status_code != 201:
            raise Exception(f"{r.status_code} 上传异常")
        imageUrl = f"https://gitee.com/{my_repo}/raw/master/{path}"

    except Exception as e:
        return "[Error] 上传图片至Gitee错误"

    try:
        print("Saving Image to json")
        
        with open(f"jm.json", "r", encoding="UTF-8") as f:
            data = json.load(f)


        data[title] = imageUrl

        with open(f"jm.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return imageUrl
    except Exception as e:
        return "[Error]"


def getJinmanAnime(num: int, myQQ: str, group_id: int):


    # try:
    #     url = f"https://jm18c-tyu.net/photo/{num}?shunt=3"
    #     with open("jm.json", 'r', encoding="UTF-8") as f:
    #         data = json.load(f)

    #     if str(num) not in data:
    #         imgUrl = saveImg(url, str(num))
    #         if imgUrl[0] == '[': raise Exception(imgUrl)
    #     else:
    #         imgUrl = data[str(num)]

    # except Exception as e:
    #     GetAndPost.postMessage(686822576, str(e))

    url = f"https://jm18c-tyu.net/photo/{num}?shunt=3"
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page = browser.new_page()
    #     try:
    #         page.goto(url, timeout= 60000, wait_until="load")  # 等待页面加载完成
    #     except Exception as e:
    #         pass
    #     png_bytes = page.screenshot(full_page=True)
    #     browser.close()

    # imgUrl = base64.b64encode(png_bytes).decode("utf-8")

    print(num)
    headers = {
        'Content-Type': 'application/json'
    }
    text = f"神秘数字{num}"
    name = f"{num}.png"
    data = {
        "group_id": 686822576,
        "messages": [
            {
                "type": "node",
                "data": {
                    "user_id": 3951373455,
                    "content": [
                        {
                            "type": "text",
                            "data": {
                                "text": "神秘数字"
                            }
                        }
                    ]
                }
            },
            {
                "type": "node",
                "data": {
                    "user_id": 3951373455,
                    "content": [
                        {
                            "type": "file",
                            "data": {
                                "file": "https://gitee.com/Cysheper/my-images/raw/master/jminfo/350236.png",
                                "name": "01.png"
                            }
                        }
                    ]
                }
            }
        ]
    }

    try:
        info = requests.post(f"http://localhost:8081/send_group_forward_msg", params=data, headers=headers, timeout=15000).json()
        if info["status"] != "ok":
            raise Exception("[Error] Post AnimeDetails Error")
    except Exception as e:
        GetAndPost.postMessage(group_id, "[Error] Post AnimeDetails Error")
        
