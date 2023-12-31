from .base import *


class IssueOpenInBrowser(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        issue_id=16,
    ):
        issue_url = f"{repo_url}/issues/{issue_id}"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 GitHub 查看更多 Issue 信息 **\n*{issue_url}*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器中打开",
                    tag="lark_md",
                    type="primary",
                    multi_url={
                        "url": issue_url,
                        "android_url": issue_url,
                        "ios_url": issue_url,
                        "pc_url": issue_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Issue Manual"),
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
    message = IssueOpenInBrowser()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
