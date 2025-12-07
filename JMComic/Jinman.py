import random
import json
import jmcomic
from jmcomic import JmModuleConfig, JmOption, JmAlbumDetail
import shutil
from GetAndPost import GetAndPost
import logging
import random
from itertools import islice
from Update2OSS import Update2OSS
import os

logging.basicConfig(
    filename='app.log',         # 日志文件名
    level=logging.INFO,         # 日志级别
    format='%(asctime)s %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S', 
    encoding='utf-8'            # 防止中文乱码
)


# Pmyname
JmModuleConfig.PFIELD_ADVICE['myname'] = lambda photo: f'{photo.id}'
client = JmOption.default().new_jm_client()

def randomSeed() -> int:
    num = random.randint(100000, 1999999)
    return num

def getJinmanImageUrlBySeed(num: int) -> tuple[str, str]:
    url = f"https://cdn-msp3.jm18c-tyu.net/media/albums/{num}.jpg"
    return url, f"神秘数字：{str(num)}"

def getJinmanImageUrlRand() -> tuple[str, str]:
    return getJinmanImageUrlBySeed(randomSeed())


def downloadJMComics(num: str) -> None:
    option = jmcomic.create_option_by_file("JMComic/option.yml")

    jmcomic.download_photo(num, option=option)

def task(group_id: int, num: str) -> None:
    GetAndPost.postMessage(group_id, f"【已开始下载】JM{num}， 请耐心等待...")

    with open("comic.json", "r", encoding="utf-8") as f:
        comic_data = json.load(f)

    if num in comic_data:
        comic_name = comic_data[num]
        print("漫画已存在，跳过下载步骤。")
    else:
        try:
            print("正在下载JM漫画...")
            downloadJMComics(num)
            page = client.search_site(search_query=num)
            album: JmAlbumDetail = page.single_album
            comic_name = album.authoroname

        except Exception as e:
            logging.error(f"Error in downloading JM comic {num}: {e}")
            GetAndPost.postMessage(group_id, f"【下载失败】JM{num}，下载过程错误")
            return
        try:
            print("正在上传JM漫画到OSS...")
            Update2OSS.upload_file(f"QQBot/JMComic/{num}.pdf", f"{num}.pdf")
            print("上传完成。")
        
        except Exception as e:
            logging.error(f"Error in downloading or uploading JM comic {num}: {e}")
            GetAndPost.postMessage(group_id, f"【下载失败】JM{num}，上传OSS过程错误")
            return

        with open("comic.json", "w", encoding="utf-8") as f:
            comic_data[num] = comic_name
            json.dump(comic_data, f, ensure_ascii=False, indent=4)
    
    url = f"https://cynite.oss-cn-guangzhou.aliyuncs.com/QQBot/JMComic/{num}.pdf"

    print("正在发送JM漫画到QQBot...")
    info = GetAndPost.postJMComic(group_id, url, comic_name, num)

    print("发送完成。")
    if info == "[Accepted]":
        GetAndPost.postMessage(group_id, f"【下载完成】JM{num}: {comic_name}")
    else:
        GetAndPost.postMessage(group_id, f"【下载失败】JM{num}，上传QQ过程错误")


    if os.path.exists(num):
        shutil.rmtree(num, ignore_errors=True)
    if os.path.exists(f"{num}.pdf"):
        os.remove(f"{num}.pdf")



if __name__ == "__main__":
    task(686822576, "350236")