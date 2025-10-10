import requests
from bs4 import BeautifulSoup
import json
from html2image import Html2Image
import markdown
from playwright.sync_api import sync_playwright
import base64
import random
import logging
from GetAndPost import GetAndPost

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)



with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

my_repo = config["GitHub_repo"]
my_token = config["GitHub_Token"]


def fetch_luogu_problem_list(difficulty=None, page=1):
    url = "https://www.luogu.com.cn/problem/list?type=luogu"
    headers = {"User-Agent": "Mozilla/5.0"}

    url += f"&difficulty={difficulty}&page={page}"

    res = requests.get(url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    script_tag = soup.find("script", id="lentille-context")
    if script_tag and script_tag.string:
        data_json = json.loads(script_tag.string)
    else:
        raise ValueError("未找到包含题目列表的 JSON 数据")
    data_json = json.loads(script_tag.string)

    data = []

    for result in data_json["data"]["problems"]["result"]:
        data.append(result["pid"])

    return data


def randomProblem(difficulty: int):
    with open(f"Problem_set/D{difficulty}-problems.json", "r", encoding="UTF-8") as f:
        data = json.load(f)

    problem = random.choice(list(data))

    return problem

def capture_webpage(url: str, save_path: str = "", full_page: bool = True):
  with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      page = browser.new_page()
      page.goto(url, wait_until="networkidle")  # 等待页面加载完成
      png_bytes = page.screenshot(full_page=full_page)
      browser.close()

  # 转 Base64
  img_base64 = base64.b64encode(png_bytes).decode("utf-8")

  # 可选保存本地
  if save_path != "":
      with open(save_path, "wb") as f:
          f.write(png_bytes)

  return img_base64



def task(pid: str):
    try:
        with open("problems.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if pid in list(data.keys()):
            return data[pid]

        try:
            url = f"https://www.luogu.com.cn/problem/{pid}"

            b64 = capture_webpage(url)

            # GitHub仓库 
            repo = my_repo

            path = f"luogu/{pid}.png"
            # api
            api = f"https://gitee.com/api/v5/repos/{repo}/contents/{path}"

            data = {
                "access_token": my_token,
                "message": f"upload {pid}", 
                "content": b64,
                "branch": "master"
            }

            r = requests.post(api, json=data)
            if r.status_code != 201:
                raise Exception(f"{r.status_code} 上传异常")
            imageUrl = f"https://gitee.com/{repo}/raw/master/{path}"

        except Exception as e:
            logging.error(f"[Error] 图片上传Gitee错误 {str(e)}")
            return "[Error] 上传图片至Gitee错误"

        try:
            
            with open("problems.json", "r", encoding="UTF-8") as f:
                data = json.load(f)


            data[pid] = imageUrl

            with open("problems.json", "w", encoding="UTF-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            return imageUrl

        except Exception as e:
            logging.error("保存图片错误")
            return "[Error] 保存图片错误"
            
    except Exception as e:
        logging.error("保存图片错误")
        return "[Error] 保存图片错误"


def shift(diff: str) -> int:
    if diff == "入门" or diff == "红题":
        return 1
    elif diff == "橙题":
        return 2
    elif diff == "黄题":
        return 3
    elif diff == "绿题":
        return 4
    elif diff == "蓝题":
        return 5
    elif diff == "紫题":
        return 6
    elif diff == "黑题":
        return 7
    else:
        return 0
    

def run(msg: str = ""):
    if msg.strip() == "":
        return task(randomProblem(random.randint(1, 8)))
        
    else:
        num = shift(msg.strip())
        if num == 0:
            return "[Error] 题目难度不存在"
        return task(randomProblem(num))