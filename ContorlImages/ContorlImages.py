import json
import logging
import random

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)


def saveImg(img: str, title: str) -> bool:

    try:
        with open("images.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if title not in data:
            data[title] = []

        st = set()
        for i in data[title]:
            st.add(i)
        st.add(img)

        data[title] = list(st)

        with open("images.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error("保存图片错误")
        return False
    
    return True


def getImg(title: str) -> str:
    try:
        with open("images.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        
        if title not in data:
            return "未找到相关图片"
        else:
            return random.choice(data[title])
        
    except Exception as e:
        return "获取图片错误"



