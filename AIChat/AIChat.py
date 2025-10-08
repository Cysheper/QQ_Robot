from openai import OpenAI
from typing import List
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam
import json
from pathlib import Path
import logging

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

with open("config.json", "r", encoding="UTF-8") as f:
    config = json.load(f)

baseURL = config["AI_BASE_URL"]
apiKey = config["AI_API_KEY"]

client = OpenAI(api_key=apiKey, base_url=baseURL)

MOD: dict = {
    "name": "bocchi",
    "content": ""
}
with open(f"CharactorsMod/{MOD["name"]}.txt", "r", encoding="UTF-8") as f:
    MOD["content"] = f.read()
    MOD["name"] = "bocchi"
    
USER = config["adminUser"]

memory: List[ChatCompletionMessageParam] = [{"role": "system", "content": MOD["content"]}]

def saveMemory(memory: List[ChatCompletionMessageParam]):
    global MOD
    with open("memories.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if len(memory) != 1:
        data[MOD["name"]] = memory
    else: 
        return False
    with open("memories.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return True

def loadMemory():
    global memory
    with open("memories.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if len(data[MOD["name"]]) == 1:
        return False
    memory = data[MOD["name"]]
    return True
    
def clean() -> bool:
    global memory
    global MOD
    saveMemory(memory)
    memory.clear()
    memory.append({"role": "system", "content": MOD["content"]})
    logging.info("记忆已清除")
    return True

def modifyMod(newMod: str) -> str:
    global MOD
    path = Path(f"CharactorsMod/{newMod}.txt")
    if path.exists():
        with open(path, "r", encoding="UTF-8") as f:
            MOD["name"] = newMod
            MOD["content"] = f.read()
    else:
        logging.error(f"模式不存在 {newMod}")
        return f"[Error] 模式不存在 {newMod}"
    clean()
    logging.info(f"已切换模式: {newMod}")
    return f"[Accepted] 已切换模式: {newMod}"
    

def zipMemory():
    global memory
    memory.append({"role": "system", "content": config["SummeryCmd"]})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=memory
    ) 
    answer = response.choices[0].message.content or ""
    memory.clear()
    memory = [{"role": "system", "content": f"[历史聊天总结]: {answer}"}]
    return answer


def ask(problem: str, user: str) -> str:
    clear = False
    if len(memory) >= 100:
        clear = True
        zipMemory()
    if problem == "清除记忆" or problem == "记忆清除":
        if clean():
            return "[Accepted] 记忆已清除"
        else:
            return "[Error] 暂无记忆可删除"
    if problem == "恢复记忆" or problem == "记忆恢复":
        if loadMemory():
            return "[Accepted] 记忆已恢复"
        else:
            return "[Error] 暂无记忆可恢复"
    try:
        memory.append({"role": "user", "content": f"UserName: {user}, Content: {problem}"})
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=memory
        ) 
        answer = response.choices[0].message.content or ""
        memory.append({"role": "assistant", "content": f"{answer}"})
        if clear:
            return "[Notice 记忆超限，已压缩记忆] " + answer
        else: return answer
    except Exception as e:
        print(f"发生错误: {str(e)}")
        logging.error(f"Error: AI 发生错误: {str(e)}")
        return f"抱歉，出现了一个错误: {str(e)}"