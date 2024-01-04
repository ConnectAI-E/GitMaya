from base import *


class PrTipCommitHistory(FeishuMessageCard):
    def __init__(
        self,
        content="",
        commit_url="https://github.com/ConnectAI-E/GitMaya/pull/17/commits/351c6b53506956a3b1c50f0a866d0289ca4077de",
    ):
        elements = [
            FeishuMessageDiv(
                content=f"[-@river - feat: add xxx]({commit_url})",
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya Pr Action"),
        ]
        header = FeishuMessageCardHeader("📚 Commit History")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = PrTipCommitHistory()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
