import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

url = config["URL"]


def getMessage(group_id: int):
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


def postMessage(group_id: int, message: str) -> bool:
    payload = {
        "group_id": group_id,
        "message": f"{message}",
    }
    info = requests.post(f"{url}/send_group_msg", data=payload).json()
    if info["status"] == "ok":
        return True
    else:
        return False