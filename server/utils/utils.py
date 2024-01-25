import httpx


def upload_image(url, bot):
    response = httpx.get(url, follow_redirects=False)
    if response.status_code == 302:
        new_url = response.headers.get("Location")
        return upload_image(new_url, bot)
    # 确保请求成功
    elif response.status_code == 200:
        return upload_image_binary(response.content, bot)
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
