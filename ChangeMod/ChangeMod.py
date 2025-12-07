from AIChat import AIChat

def changeMod(message):
    if message == "默认":
        answer = AIChat.modifyMod("Default")
    elif message == "猫娘":
        answer = AIChat.modifyMod("CatGirl")
    elif message == "算法大佬" or message == "算竞大佬" or message == "算法学长":
        answer = AIChat.modifyMod("CS-Master")
    elif message == "初音" or message == "初音未来" or message == "miku":
        answer = AIChat.modifyMod("Miku")
    elif message == "后藤一里" or message == "波奇" or message == "bocchi":
        answer = AIChat.modifyMod("bocchi")
    elif message == "孙笑川":
        answer = AIChat.modifyMod("sun")
    elif message == "特朗普" or message == "川普":
        answer = AIChat.modifyMod("trump")
    elif message[:2] == "切换":
        answer = "[Error] 不存在的模式"
    return answer