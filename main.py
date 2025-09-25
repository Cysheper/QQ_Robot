import requests
import json
import random
import time
from AIChat import AIChat

url = "http://localhost:3001"

group_ids = [935593102, 1062349114]

group_id = 935593102


def getMessage():
    payload = {
        "group_id": group_id,
        "message_seq": "",
        "count": 1,
        "reverseOrder": "false"
    }
    try:
        data = requests.get(f"{url}/get_group_msg_history", params=payload).json()["data"]
    except Exception as e:
        return "Unkown Error"

    message = []
    if len(data["messages"]) >= 1:
        message = data["messages"][0]["message"]
    else: 
        message = "None Messages"
    return message


def postMessage(message) -> bool:
    payload = {
        "group_id": group_id,
        "message": f"{message}",
    }
    info = requests.post(f"{url}/send_group_msg", data=payload).json()
    if info["status"] == "ok":
        return True
    else:
        return False


def chouqian() -> str:
    num = random.randint(1, 11)
    if num == 1:
        return "大吉"
    elif num <= 4:
        return "小吉"
    elif num <= 7:
        return "中平"
    elif num <= 9:
        return "小凶"
    else:
        return "大凶"


def task():
    message = getMessage()
    print(message)
    if len(message) >= 22 and message[:21] == "[CQ:at,qq=3845964398]":
        message = message[22:]
        print(message)
    else: 
        print("Passed Info")
        return
    answer = "你刚才说了：" + message
    if not postMessage(answer):
        print("Post Error")

if __name__ == '__main__':
    idx = 0
    while True:
        idx %= len(group_ids)
        group_id = group_ids[idx]
        task()
        time.sleep(1)
        idx += 1

        
