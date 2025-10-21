import random
import json
import jmcomic
from jmcomic import JmModuleConfig, JmOption, JmAlbumDetail

import shutil
from GetAndPost import GetAndPost

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
    downloadJMComics(num)
    page = client.search_site(search_query=num)
    album: JmAlbumDetail = page.single_album
    comic_name = album.authoroname
    info = GetAndPost.postJMComic(group_id, num, comic_name)
    if info == "[Accepted]":
        GetAndPost.postMessage(group_id, f"【下载完成】JM{num}: {comic_name}")
    else:
        GetAndPost.postMessage(group_id, f"【下载失败】JM{num}: {comic_name}")
    shutil.rmtree(num, ignore_errors=True)
    import os
    os.remove(f"{num}.pdf")

if __name__ == "__main__":
    task(686822576, "350236")