import asyncio
import logging

from connectai.lark.sdk import Bot
from httpx import AsyncClient
from urllib3 import encode_multipart_formdata


class ChunkedDownloader(object):
    def __init__(
        self,
        chunk_size=1 * 1024**2,
        max_chunk=10,
        timeout=10,
        proxy=None,
        proxies=None,
    ):
        self.chunk_size = chunk_size
        self.max_chunk = max_chunk
        self.timeout = timeout
        self.proxy = proxy  # 废弃的参数
        self.proxies = proxies

    @property
    def client(self):
        # 尝试使用tornado的httpclient，底层是curlasynchttpclient
        return AsyncClient()
        # return httpx.AsyncClient(proxies=self.proxies)

    async def get_content_length(self, url):
        async with self.client as client:
            response = await client.head(url)
            if response.status_code >= 300:
                raise Exception()
            return (
                int(response.headers.get("content-length")),
                response.headers.get("accept-ranges", "") == "bytes",
            )

    def parts_generator(self, size, start=0, part_size=1 * 1024**2):
        while size - start > part_size:
            yield start, start + part_size - 1
            start += part_size
        yield start, size

    async def download_chunk(self, url, headers):
        logging.debug("download %r %r", url, headers)
        try:
            async with self.client as client:
                response = await client.get(url, headers=headers, timeout=self.timeout)
                return response.content
        except Exception as e:
            logging.error(e)
            async with self.client as client:
                response = await client.get(url, headers=headers, timeout=self.timeout)
                return response.content

    async def download(self, url):
        try:
            size, support_range = await self.get_content_length(url)
        except Exception as e:
            size, support_range = await self.get_content_length(url)
        chunk_size = self.chunk_size
        if size / self.chunk_size > self.max_chunk:
            chunk_size = int((size + self.max_chunk + 1) / self.max_chunk)
        tasks = []
        for number, sizes in enumerate(
            self.parts_generator(size, part_size=chunk_size if support_range else size)
        ):
            tasks.append(
                self.download_chunk(url, {"Range": f"bytes={sizes[0]}-{sizes[1]}"})
            )
        logging.info("download file %r in %r chunks", url, len(tasks))
        result = await asyncio.gather(*tasks)
        return b"".join(result)


async def upload_image(img_url, bot):
    # https://open.feishu.cn/document/server-docs/im-v1/image/create
    try:
        # file_response = await AsyncHTTPClient().fetch(img_url, request_timeout=60)
        file_content = await ChunkedDownloader.download(img_url)
    except Exception as e:
        logging.exception(e)
        file_content = await ChunkedDownloader.download(img_url)
    logging.info("download file %r %r", img_url, len(file_content))
    return await upload_image_binary(file_content, bot)


async def upload_image_binary(img_bin, bot):
    url = f"{bot.HOST}/open-apis/im/v1/images"
    response = bot.post(url, json={"image_type": "message", "image": img_bin}).json()
    return response["data"]["image_key"]


def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
