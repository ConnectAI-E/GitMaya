from .base import *


class ChatActionChoose(FeishuMessageCard):
    def __init__(
        self,
        content="",
        actions=[],
        action_url="https://github.com/ConnectAI-E/GitMaya/actions",
    ):
        elements = [
            FeishuMessageDiv(
                content=f"** 🚀 运行 Action **\n*{action_url}*",
                tag="lark_md",
                extra=FeishuMessageSelect(
                    *[FeishuMessageOption(value=action) for action in actions],
                    placeholder="选择想要执行的Action",
                    value={
                        "key": "value",  # TODO
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Chat Action"),
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
    message = ChatActionChoose(actions=["aaa", "bbb"])
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
