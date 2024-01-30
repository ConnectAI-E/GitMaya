import logging

import httpx
from utils.redis import stalecache


# 使用 stalecache 装饰器，以 url 作为缓存键
@stalecache(expire=300, stale=600)
def upload_image(url, bot):
    logging.info("upload image: %s", url)
    response = httpx.get(url, follow_redirects=True)
    if response.status_code == 200:
        # 函数返回值: iamg_key 存到缓存中
        img_key = upload_image_binary(response.content, bot)
        return img_key
    else:
        return None


def upload_image_binary(img_bin, bot):
    url = f"{bot.host}/open-apis/im/v1/images"

    data = {"image_type": "message"}
    files = {
        "image": img_bin,
    }
    response = bot.post(url, data=data, files=files).json()
    return response["data"]["image_key"]


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
