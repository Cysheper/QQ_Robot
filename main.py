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
import requests
from DouBao import DouBao
from DailyProblem import DailyProblem
from JMComic import Jinman
from UserApi import delList

# 加载配置文件

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

lastTime = None
lastImg = None

def configMessage(messages, myQQ):
    hasAtMe, message = False, " "
    replyID = None
    for msg in messages:
        if msg['type'] == 'at' and msg['data']['qq'] == myQQ:
            hasAtMe = True
        elif msg['type'] == 'text':
            message += msg['data']['text'] + " "
        elif msg['type'] == 'reply':
            replyID = msg['data']['id']
    message = message.strip()
    return hasAtMe, message, replyID

def routers(message, sender, replyID, group_id):
    image_url, respond = None, None
    if replyID != None:
        msg, img = GetAndPost.getReply(replyID)
        if msg != None: message += " " + msg


    if message[:2] == "切换":
        respond = ChangeMod.changeMod(message[2:].strip())


    elif message[:2] == "添加" and img != None:
        if type(img) == str:
            respond = ContorlImages.saveImg(img, message[2:].strip())
        else:
            respond = ContorlImages.saveImgByGroup(img, message[2:].strip())


    elif message[:2] == "来只":
        image_url = ContorlImages.getImg(message[2:].strip())
        if image_url == "未找到相关图片" or image_url == "获取图片错误":
            respond = image_url
            image_url = None
            
            
    elif message[:4] == "图片信息":
        respond = ContorlImages.getImgInfo()

    elif message[:2] == "删除" and img != None:
        respond = ContorlImages.delImg(img, message[2:].strip())


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
4、删除[图片类别] - 从指定类别中删除引用的图片
5、清除记忆 - 清除当前记忆
6、恢复记忆 - 恢复前两次清除记忆之间的记忆，超过两次清除的记忆永久删除
7、洛谷 - 随机难度洛谷题目，需要一定加载时间 （洛谷题目每两分钟是同一题）
8、洛谷[难度] - 指定难度洛谷题目，根据颜色划分，红题、橙题、黑题什么的（洛谷题目每两分钟是同一题）
8、除了上述指令外，其余指令将由AI接管回答，AI不知道其余指令，AI不可发出其余指令
"""
        respond = msg


    elif message[:2] == "洛谷":
        global lastImg
        if problemLimit():
            image_url = DailyProblem.run(message[2:])
            if image_url != "[Error] 题目难度不存在":
                lastImg = image_url
        else:
            if lastImg != None: 
                image_url = lastImg


    elif message[:2] == "禁漫" and message[2:].strip() == "":
        image_url, respond = Jinman.getJinmanImageUrlRand()


    elif message[:2] == "禁漫" and message[2:].strip().isdigit():
        image_url, respond = Jinman.getJinmanImageUrlBySeed(int(message[2:].strip()))

    elif message[:6] == "撤回名单展示":
        respond = delList.showDel()
    
    elif message[:6] == "撤回名单添加":
        respond = delList.addDel(message[6:].strip())

    elif message[:6] == "撤回名单删除":
        respond = delList.moveDel(message[6:].strip())

    elif message[:4] == "禁漫下载":
        Jinman.task(group_id, message[4:].strip())

    elif replyID != None and img != None:
        respond = DouBao.ask_vision(img, message, sender)


    else: respond = AIChat.ask(message, sender)


    return respond, image_url


def problemLimit() -> bool:
    global lastTime, lastImg
    now = time.time()
    if lastTime == None or lastImg == None or now - lastTime > 30 * 60:
        lastTime = now
        return True
    else:
        return False


def task(id: int, message, sender, replyID):
    print("task running")

    answer, image = routers(message, sender, replyID, id)


    if answer != None and image == None:
        if not GetAndPost.postMessage(id, answer):
            logging.error(f"PostMessage Error : {message}")
            print("[PostMessage Error]")


    if image != None and answer == None:
        if message[2:] in delList.List:
            msg = GetAndPost.postImg(id, image, True)

        else: msg = GetAndPost.postImg(id, image, False)

        if msg != "[Accepted]":
            logging.error(f"PostImage Error : {message}")
            print("[PostImage Error]")
            if not GetAndPost.postMessage(id, msg):
                logging.error(f"PostMessage Error : {message}")
                print("[PostMessage Error]")


    if image != None and answer != None:
        msg = GetAndPost.postImgAndMessage(id, image, answer)
        if msg != "[Accepted]":
            logging.error(f"PostImage Error : {message}")
            print("[PostImage Error]")
            if not GetAndPost.postMessage(id, msg):
                logging.error(f"PostMessage Error : {message}")
                print("[PostMessage Error]")        

    print("task end")

def checkInfo(messages, myQQ):
    if messages == "GetMessage Error":
        logging.error(f"GetMessage Error")
        print("[GetMessage Error]")
        return None, None, None, None
    
    if messages == []:
        return None, None, None, None
    
    sender = messages[0]["sender"]["nickname"]
    message_id = messages[0]["message_id"]
    messages = messages[0]["message"]
    hasAtMe, message, replyID = configMessage(messages, myQQ)
    
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


def pushMessage(message_queue, myQQ):
    idx = 0
    group_ids = GetGroupsId.getGroupsId()
    lastMessage = dict()
    while True:
        idx %= len(group_ids)
        group_id = group_ids[idx]
        messages = GetAndPost.getMessage(group_id)
        message, sender, replyID, message_id = checkInfo(messages, myQQ)
        # print(f"group_id={group_id},message={message},sender={sender},replyID={replyID}")

        if message == None or sender == None:
            time.sleep(0.2)
            idx += 1
            continue
        
        if group_id not in lastMessage:
            lastMessage[group_id] = 0

        if lastMessage[group_id] != message_id:
            message_queue.put((group_id, message, sender, replyID))
            lastMessage[group_id] = message_id
            
        time.sleep(0.2)
        idx += 1

def main() -> None:
    global myQQ
    myQQ = str(GetGroupsId.getQQId())
    logging.info(myQQ)
    print(myQQ)
    message_queue = queue.Queue()
    pushMessageThread = threading.Thread(target=pushMessage, args=(message_queue,myQQ), daemon=True)
    runThread = threading.Thread(target=run, args=(message_queue,), daemon=True)
    pushMessageThread.start()
    runThread.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
        
