from openai import OpenAI
from typing import List
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam
import json
from pathlib import Path
import logging
from AIChat import AIChat

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
apiKey = config["DOUBAO_AI_API_KEY"]

client = OpenAI(api_key=apiKey, base_url=baseURL)

def ask_vision(img_url: str, problem: str, user: str) -> str:
    try:
        AIChat.memory.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_url
                    },
                },
                {"type": "text", "text": f"UserName: {user}, Content: {problem}"},
            ],
        })
        response = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
            model="doubao-seed-1-6-flash-250828",
            messages=AIChat.memory
        )
        answer = response.choices[0].message.content or ""
        AIChat.memory.append({"role": "assistant", "content": f"{answer}"})

        return answer
    except Exception as e:
        print(f"发生错误: {str(e)}")
        logging.error(f"Error: AI 发生错误: {str(e)}")
        return f"[Error] Doubao API 异常"
