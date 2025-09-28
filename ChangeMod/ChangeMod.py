from AIChat import AIChat

def changeMod(message):
    if message == "切换默认":
        answer = AIChat.modifyMod("Default")
    elif message == "切换猫娘":
        answer = AIChat.modifyMod("CatGirl")
    elif message == "切换算法大佬" or message == "切换算竞大佬" or message == "切换算法学长":
        answer = AIChat.modifyMod("CS-Master")
    elif message == "切换初音" or message == "切换初音未来" or message == "切换miku":
        answer = AIChat.modifyMod("Miku")
    elif message[:2] == "切换":
        answer = "[Error] 不存在的模式"
    return answer