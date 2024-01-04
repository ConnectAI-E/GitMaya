from base import *


class PrTipSuccess(FeishuMessageCard):
    def __init__(
        self,
        content="",
        action_detail_url="https://github.com/ConnectAI-E/GitMaya/actions/runs/7406888938",
    ):
        elements = [
            FeishuMessageDiv(
                content=f'1. 已修改 Issue 标题为 "sss"\n2. 已分配任务给 @xx\n3. 已关闭 issue\n\n \n[查看更多WorkFlow运行信息](action_detail_url)',
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya Chat Action"),
        ]
        header = FeishuMessageCardHeader("🚀 Action 运行结果")
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
