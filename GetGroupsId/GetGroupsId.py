import requests
import json
import logging

with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

url = config["URL"]

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

def getGroupsId() -> list:
    payload = {
        "no_cache": False
    }
    try:
        respond = requests.post(f"{url}/get_group_list", params=payload).json()
        data = respond["data"]
    except Exception as e:
        logging.error(f"获取群列表错误：{str(e)}")

    groups = []

    for item in data:
        groups.append(item["group_id"])
    return groups

def getQQId():
    try:
        respond = requests.post(f"{url}/get_login_info", data={}).json()
        
    except Exception as e:
        logging.error("获取用户QQ错误")

    if respond["status"] == "ok":
        return respond["data"]["user_id"]
    return "获取QQ号错误"