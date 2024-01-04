from base import *


class ChatTipFailed(FeishuMessageCard):
    def __init__(
        self,
        content="没有执行此操作的权限\n\n(这里说明操作失败的原因)",
    ):
        elements = [
            FeishuMessageDiv(
                content=content,
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya Chat Action"),
        ]
        header = FeishuMessageCardHeader("😕 操作失败！")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = ChatTipFailed()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
