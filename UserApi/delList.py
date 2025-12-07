


List: set[str] = {"大雷", "小雷", "白丝", "黑丝", "色图", "涩图"}


def addDel(key_word: str) -> str:

    List.add(key_word)

    return f"[Accepted] 添加 {key_word} 至撤回名单成功"


def showDel() -> str:
    return f"撤回名单：{str(list(List))}"

def moveDel(key_word: str) -> str:

    if key_word not in List:
        return f"[Error] {key_word}不在撤回名单中"
    
    List.remove(key_word)

    return f"[Accepted] 删除 {key_word} 成功"



