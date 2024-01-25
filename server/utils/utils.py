import httpx


def upload_image(url, application_id):
    response = httpx.get(url)
    # 确保请求成功
    if response.status_code == 200:
        return upload_image_binary(response.content, application_id)
    else:
        return None


def upload_image_binary(img_bin, application_id):
    from tasks.lark.base import get_bot_by_application_id

    bot, _ = get_bot_by_application_id(application_id)
    url = f"{bot.HOST}/open-apis/im/v1/images"
    response = bot.post(url, json={"image_type": "message", "image": img_bin}).json()
    return response["data"]["image_key"]


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
