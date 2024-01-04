from base import *


class ManageSuccess(FeishuMessageCard):
    def __init__(
        self,
        content="",
    ):
        elements = [
            FeishuMessageDiv(
                content=content,
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya Manage Action"),
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
    message = ManageSuccess(
        "1. 成功创建了名为「feishu-openai 项目群」的新项目群。\n2. 已向 @river 和 @zoe 发送邀请，等待其加入群聊。"
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
