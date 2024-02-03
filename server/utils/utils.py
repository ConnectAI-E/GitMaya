import logging

import httpx
from utils.redis import stalecache


# 使用 stalecache 装饰器，以 url 作为缓存键
@stalecache(expire=3600, stale=600)
def upload_image(url, bot):
    logging.info("upload image: %s", url)
    if not url or not url.startswith("http"):
        return ""
    response = httpx.get(url, follow_redirects=True)
    if response.status_code == 200:
        # 函数返回值: iamg_key 存到缓存中
        img_key = upload_image_binary(response.content, bot)
        return img_key
    else:
        return ""


@stalecache(expire=86400, stale=600)
def upload_private_image(url, access_token, bot):
    img_bin = download_image_with_token(access_token, url)
    if img_bin:
        img_key = upload_image_binary(img_bin, bot)
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


def download_image_with_token(access_token: str, url: str) -> str | None:
    """Download image by access token.

    Args:
        access_token (str): The user access token.
        url (str): The image url.

    Returns:
        str: image.
    """

    response = httpx.get(
        url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        follow_redirects=True,
    )

    if response.status_code != 200:
        logging.debug(f"Failed to get image. {response.text}")
        return None

    return response.content


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
