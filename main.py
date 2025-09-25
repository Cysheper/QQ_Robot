from AIChat import AIChat
from GetAndPost import GetAndPost
from typing import List, Dict, Any
import json
import time
import logging

# 加载配置文件
with open("config.json", "r") as f:
    config = json.load(f)

group_ids = config["group_ids"]
group_id = group_ids[0]
myQQ = config["myQQ"]

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

def task(id: int):
    messages = GetAndPost.getMessage(id)
    hasAtMe = False
    message = " "
    print(messages)
    for info in messages:
        if isinstance(info, dict) and info['type'] == 'at' \
            and info['data']['qq'] == myQQ:
            for msg in messages:
                if isinstance(msg, dict) and msg.get('type') == 'text':
                    hasAtMe = True
                    message += msg['data']['text'] + " "
                    break
            break
    message.strip()
    if not hasAtMe:
        logging.info(f"passed info : {message}")
        print(f"passed info : {message}")
    else:
        answer = "你刚才说了：" + message
        if not GetAndPost.postMessage(id, answer):
            print("Post Error")

if __name__ == '__main__':
    idx = 0
    while True:
        idx %= len(group_ids)
        group_id = group_ids[idx]
        task(group_id)
        time.sleep(1)
        idx += 1

        
