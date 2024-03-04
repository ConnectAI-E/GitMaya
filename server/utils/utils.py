import logging
import os

import httpx
from utils.redis import stalecache


def process_image(url, bot):
    if not url or not url.startswith("http"):
        return ""

    if url.startswith(f"{os.environ.get('DOMAIN')}/api"):
        return url.split("/")[-1]
    return upload_image(url, bot)


# 使用 stalecache 装饰器，以 url 作为缓存键
@stalecache(expire=3600, stale=600)
def upload_image(url, bot):
    logging.info("upload image: %s", url)
    response = httpx.get(
        url, follow_redirects=True, timeout=15
    )  # Increase the timeout to 30 seconds
    if response.status_code == 200:
        # 函数返回值: iamg_key 存到缓存中
        img_key = upload_image_binary(response.content, bot)
        return img_key
    else:
        return ""


def upload_image_binary(img_bin, bot):
    url = f"{bot.host}/open-apis/im/v1/images"

    data = {"image_type": "message"}
    files = {
        "image": img_bin,
    }
    response = bot.post(url, data=data, files=files).json()
    return response["data"]["image_key"]


@stalecache(expire=3600, stale=600)
def download_file(file_key, message_id, bot, file_type="image"):
    """
    获取消息中的资源文件，包括音频，视频，图片和文件，暂不支持表情包资源下载。当前仅支持 100M 以内的资源文件的下载
    """
    # open-apis/im/v1/images/{img_key} 接口只能下载机器人自己上传的图片
    url = f"{bot.host}/open-apis/im/v1/messages/{message_id}/resources/{file_key}?type={file_type}"

    response = bot.get(url)
    return response.content


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
