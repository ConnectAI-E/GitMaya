import logging

import httpx


def upload_image(url, application_id):
    response = httpx.get(url, follow_redirects=False)
    if response.status_code == 302:
        new_url = response.headers.get("Location")
        return upload_image(new_url, application_id)
    # 确保请求成功
    elif response.status_code == 200:
        logging.info(f"image_bin: {response.content}")
        return upload_image_binary(response.content, application_id)
    else:
        return None


def upload_image_binary(img_bin, application_id):
    from tasks.lark.base import get_bot_by_application_id

    bot, _ = get_bot_by_application_id(application_id)
    url = f"{bot.host}/open-apis/im/v1/images"

    files = {
        "image_type": "message",
        "image": (img_bin, "image/png"),
    }
    response = bot.post(url, files=files).json()
    return response["data"]["image_key"]


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
