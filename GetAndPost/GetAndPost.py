import requests
import json
import logging
import base64

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

def getMessage(group_id: int, count=1):
    payload = {
        "group_id": group_id,
        "message_seq": "",
        "count": count,
        "reverseOrder": "false"
    }
    try:
        data = requests.get(f"{url}/get_group_msg_history", params=payload).json()["data"]["messages"]
    except Exception as e:
        logging.error(f"GetMessage Error: {str(e)}")
        return "GetMessage Error"

    messages = []

    for msg in data:
        messages.append({
            "message_id": msg["message_id"],
            "sender": {
                "nickname": msg["sender"]["nickname"]
            },
            "message": msg["message"]
        })
    return messages


def postMessage(group_id: int, message: str) -> bool:
    payload = {
        "group_id": group_id,
        "message": f"{message}",
    }
    try:
        info = requests.post(f"{url}/send_group_msg", data=payload).json()
    except Exception as e:
        logging.error(f"Network Error: {str(e)}")
 
    if info["status"] == "ok":
        return True
    else:
        logging.error("PostMessage Error")
        return False
    

def getReply(group_id: int):
    payload = {
        "message_id": group_id
    }
    try:
        data = requests.get(f"{url}/get_msg", params=payload).json()
        data = data["data"]
    except Exception as e:
        logging.error(f"GetMessage Error: {str(e)}")
        return "GetMessage Error", ""
    message, img = "", ""
    for msg in data['message']:
        if msg['type'] == "text": message += msg['data']['text']
        if msg['type'] == 'image':  img = msg['data']['url']
    return message, img


def postImg(group_id: int, img: str) -> str:
    payload = {
        "group_id": group_id,
        "message": [
            {
                "type": "image",
                "data": {
                    "summary": "[图片]",
                    "url": img
                }
            }
        ]
    }
    try:
        info = requests.post(f"{url}/send_group_msg", json=payload).json()
    except Exception as e:
        logging.error(f"Network Error: {str(e)}")
        return "Network Error"
    if info["status"] == "ok":
        return "[Accepted]"
    else:
        logging.error("PostImg Error")
        return "[Error] Post Image Error"
