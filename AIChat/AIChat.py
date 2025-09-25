from openai import OpenAI
from typing import List
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam

baseURL = "https://api.deepseek.com"
apiKey = "sk-a4b0498a53b140859274a4ea956e8540"

client = OpenAI(api_key=apiKey, base_url=baseURL)

defaltInfo = "你是AI助手，简洁明了地回答所有问题"


memory: List[ChatCompletionMessageParam] = [{"role": "system", "content": defaltInfo}]

def clean():
    memory.clear()
    memory.append({"role": "system", "content": defaltInfo})

def ask(problem: str) -> str:
    clear = False
    if len(memory) >= 20:
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
        return f"抱歉，出现了一个错误: {str(e)}"