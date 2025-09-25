import requests
import json
import logging

with open("config.json", "r") as f:
    config = json.load(f)

url = config["URL"]
headers = {
    "Authorization": config["Token"]
}

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

def getMessage(group_id: int):
    payload = {
        "group_id": group_id,
        "message_seq": "",
        "count": 1,
        "reverseOrder": "false"
    }
    try:
        data = requests.get(f"{url}/get_group_msg_history", headers=headers, params=payload).json()
        data = data["data"]
    except Exception as e:
        logging.error(f"GetMessage Error: {str(e)}")
        return "GetMessage Error"

    message = []
    if len(data["messages"]) >= 1:
        message = data["messages"][0]["message"]
    else: 
        message = "None Messages"
    return message


def postMessage(group_id: int, message: str) -> bool:
    payload = {
        "group_id": group_id,
        "message": f"{message}",
    }
    try:
        info = requests.post(f"{url}/send_group_msg", data=payload, headers=headers).json()
    except Exception as e:
        logging.error("Network Error")
 
    if info["status"] == "ok":
        return True
    else:
        logging.error("PostMessage Error")
        return False