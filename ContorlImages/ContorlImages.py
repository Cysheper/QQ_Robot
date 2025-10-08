import json
import logging
import random
import requests
import base64
import time
from pathlib import Path
from GetAndPost import GetAndPost
import hashlib

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


def saveImg(img: str, title: str) -> str:
    try:
        # 获取图片数据
        response = requests.get(img)
        img_data = response.content
        # 转化为Base64
        b64 = base64.b64encode(img_data).decode('utf-8')
        img_hash = hashlib.md5(img_data).hexdigest()
    except Exception as e:
        logging.error("[Error] 下载图片错误")
        return "[Error] 下载图片错误"
    try:
        # 获取时间戳
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # 例如 20251007_235959
        # GitHub仓库 
        repo = my_repo
        filename = f"{title}_{timestamp}"

        # 图片格式
        content_type = response.headers.get("Content-Type", "")
        if "/" in content_type:
            ext = content_type.split("/")[-1]
        else:
            ext = "png"  # 默认兜底
        # 某些服务器可能返回 image/jpg，要统一成 jpeg
        if ext == "jpg":
            ext = "jpeg"

        path = f"QQBotUpload/{filename}.{ext}"
        # api
        api = f"https://gitee.com/api/v5/repos/{repo}/contents/{path}"

        data = {
            "access_token": my_token,
            "message": f"upload {filename}", 
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
        print(title)
        
        with open("images.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if title not in data:
            data[title] = { }

        data[title][imageUrl] = img_hash

        with open("images.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error("保存图片错误")
        return "[Error] 保存图片错误"
    
    logging.info(f"[Accepted] 添加{title}成功")
    return f"[Accepted] 添加{title}成功"


def getImg(title: str) -> str:
    try:
        with open("images.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        
        if title not in data or data[title] == { }:
            return "未找到相关图片"
        else:
            return random.choice(list(data[title].keys()))
        
    except Exception as e:
        return "获取图片错误"


def delImg(img: str, repo: str) -> str:
    try:
        with open("images.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        def get_image_hash(url):
            img_bytes = requests.get(url).content
            return hashlib.md5(img_bytes).hexdigest()  # 也可以用 sha1()

        delImg = get_image_hash(img)
                
        for url in data[repo].keys():
            if delImg == data[repo][url]:
                del data[repo][url]
                with open("images.json", "w", encoding="UTF-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                return "[Accepted] 删除图片成功"
            
        return "[Error] 图片不存在"
    except Exception as e:
        logging.error("[Error] 删除图片错误")
        return "[Error] 删除图片错误"
    

