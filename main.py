from AIChat import AIChat
from GetAndPost import GetAndPost
from GetGroupsId import GetGroupsId
from ChangeMod import ChangeMod
from ContorlImages import ContorlImages
import json
import time
import logging
import threading
import queue

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
        answer = ChangeMod.changeMod(message[2:].strip())
    elif message[:2] == "添加" and img != None:
        answer = ContorlImages.saveImg(img, message[2:].strip())
    elif message[:2] == "来只":
        answer = ContorlImages.getImg(message[2:].strip())
        if answer != "未找到相关图片" and answer != "获取图片错误":
            isImage = True
    elif message[:2] == "删除" and img != None:
        answer = ContorlImages.delImg(img, message[2:].strip())
    elif message == "help":
        msg = """指令指南
                所有指令只能@后才生效。
                【指令集】
                1、切换[角色名称] - AI身份改变为指定角色，之前角色记忆自动保存。
                初始角色[后藤一里](孤独摇滚女主)，唤醒别名[波奇][bocchi]。
                目前可以切换的角色：
                [初音未来]别名[初音][miku]
                [孙笑川]
                [特朗普]别名[川普]
                [算法大佬]别名[算竞大佬][算法学长]
                [猫娘]
                2、添加[图片类别] - 引用一张图片后可将图片保存在指定类别
                3、来只[图片类别] - 从指定类别中随机抽取一张图片
                """
        answer = msg
    else: answer = AIChat.ask(message, sender)
    return answer, isImage

def task(id: int, message, sender, replyID):
    print("task running")
    answer, isImage = routers(message, sender, replyID)
    if not isImage:
        if not GetAndPost.postMessage(id, answer):
            logging.error(f"PostMessage Error : {message}")
            print("[PostMessage Error]")
    else:
        if not GetAndPost.postImg(id, answer):
            logging.error(f"PostImage Error : {message}")
            print("[PostImage Error]")

    print("task end")

def checkInfo(messages):
    if messages == "GetMessage Error":
        logging.error(f"GetMessage Error")
        print("[GetMessage Error]")
        return None, None, None, None
    
    if messages == []:
        return None, None, None, None
    
    sender = messages[0]["sender"]["nickname"]
    message_id = messages[0]["message_id"]
    messages = messages[0]["message"]
    hasAtMe, message, replyID = configMessage(messages)
    
    if hasAtMe:
        message = message.strip()
        return message, sender, replyID, message_id
    else:
        return None, None, None, None
    

def run(message_queue):
    while True:
        group_id, message, sender, replyID = message_queue.get()
        print(f"group_id={group_id},message={message},sender={sender},replyID={replyID}")
        taskThread = threading.Thread(target=task, args=(group_id, message, sender, replyID), daemon=True)
        taskThread.start()

def pushMessage(message_queue):
    idx = 0
    group_ids = GetGroupsId.getGroupsId()
    lastMessage = None
    while True:
        idx %= len(group_ids)
        group_id = group_ids[idx]
        messages = GetAndPost.getMessage(group_id)
        message, sender, replyID, message_id = checkInfo(messages)
        # print(f"group_id={group_id},message={message},sender={sender},replyID={replyID}")

        if message == None or sender == None or replyID == None: 
            time.sleep(0.2)
            idx += 1
            continue

        if lastMessage != message_id:
            message_queue.put((group_id, message, sender, replyID))
            lastMessage = message_id
            
        time.sleep(0.2)
        idx += 1


if __name__ == '__main__':
    message_queue = queue.Queue()
    pushMessageThread = threading.Thread(target=pushMessage, args=(message_queue,), daemon=True)
    runThread = threading.Thread(target=run, args=(message_queue,), daemon=True)
    pushMessageThread.start()
    runThread.start()

    while True:
        time.sleep(1)
        
