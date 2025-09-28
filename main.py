from AIChat import AIChat
from GetAndPost import GetAndPost
from GetGroupsId import GetGroupsId
from ChangeMod import ChangeMod
from ContorlImages import ContorlImages
import json
import time
import logging

# 加载配置文件
with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

myQQ = config["myQQ"]

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

def configMessage(messages):
    hasAtMe, message = False, " "
    replyID = ""
    for msg in messages:
        if msg['type'] == 'at' and msg['data']['qq'] == myQQ:
            hasAtMe = True
        elif msg['type'] == 'text':
            message += msg['data']['text'] + " "
        elif msg['type'] == 'reply':
            replyID = msg['data']['id']
    message = message.strip()
    return hasAtMe, message, replyID

def routers(message, sender, replyID):
    isImage = False
    if replyID != "":
        msg, img = GetAndPost.getReply(replyID)
        message += " " + msg
    if message[:2] == "切换":
        answer = ChangeMod.changeMod(message)
    elif message[:2] == "添加" and img != None:
        if ContorlImages.saveImg(img, message[2:].strip()):
            answer = "[Accepted]"
        else: answer = "[Error] 添加失败"
    elif message[:2] == "来只":
        answer = ContorlImages.getImg(message[2:].strip())
        if answer != "未找到相关图片" and answer != "获取图片错误":
            isImage = True
    elif message == "help":
        pass
    else: answer = AIChat.ask(message, sender)
    return answer, isImage

def task(id: int):
    messages = GetAndPost.getMessage(id)

    if messages == "GetMessage Error":
        logging.error(f"GetMessage Error")
        print("[GetMessage Error]")
        return 
    
    if messages == []:
        return 

    sender = messages[0]["sender"]["nickname"]
    messages = messages[0]["message"]

    hasAtMe, message, replyID = configMessage(messages)
    message = message.strip()
    if hasAtMe:
        answer, isImage = routers(message, sender, replyID)
        if not isImage:
            if not GetAndPost.postMessage(id, answer):
                logging.error(f"PostMessage Error : {message}")
                print("[PostMessage Error]")
        else:
            if not GetAndPost.postImg(id, answer):
                logging.error(f"PostImage Error : {message}")
                print("[PostImage Error]")


if __name__ == '__main__':
    idx, cnt = 0, 0
    group_ids = []
    while True:
        if cnt % 240 == 0:
            group_ids = GetGroupsId.getGroupsId()
            cnt %= 240
        idx %= len(group_ids)
        group_id = group_ids[idx]
        task(group_id)
        time.sleep(0.5)
        idx += 1
        cnt += 1

        
