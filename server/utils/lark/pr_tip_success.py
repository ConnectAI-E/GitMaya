from base import *


class PrTipSuccess(FeishuMessageCard):
    def __init__(
        self,
        content='1. 已修改 Pr 标题为 "sss"\n2. 已分配任务给 @xx\n3. 已合并 pr\n',
    ):
        elements = [
            FeishuMessageDiv(
                content=content,
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya Pr Action"),
        ]
        header = FeishuMessageCardHeader("🎉 操作成功！")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = PrTipSuccess()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
