from openai import OpenAI
from typing import List
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam
import json
import logging

with open("config.json", "r") as f:
    config = json.load(f)

baseURL = config["AI_BASE_URL"]
apiKey = config["AI_API_KEY"]

client = OpenAI(api_key=apiKey, base_url=baseURL)

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)

defaultAIInfo = config["defaultAIInfo"]


memory: List[ChatCompletionMessageParam] = [{"role": "system", "content": defaultAIInfo}]

def clean():
    memory.clear()
    memory.append({"role": "system", "content": defaultAIInfo})
    logging.info("记忆已清除")

def ask(problem: str) -> str:
    clear = False
    if len(memory) >= 50:
        clear = True
        clean()
    if problem == "清除记忆":
        clean()
        return "记忆已清除"
    try:
        memory.append({"role": "user", "content": problem})
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=memory
        ) 
        answer = response.choices[0].message.content or ""
        memory.append({"role": "assistant", "content": answer})
        if clear:
            return "【记忆超限，已清除】" + answer
        else: return answer
    except Exception as e:
        print(f"发生错误: {str(e)}")
        logging.error(f"AI 发生错误: {str(e)}")
        return f"抱歉，出现了一个错误: {str(e)}"