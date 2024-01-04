from connectai.lark.sdk import *


class IssueOpenInBrowser(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        issue_id=16,
    ):
        issue_url = f"{repo_url}/issues/{issue_id}"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 Github 查看更多 Issue 信息 **\n*{issue_url}*",
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
            FeishuMessageNote(
                FeishuMessageImage(
                    img_key="img_v3_026k_3b6ce6be-4ede-46b0-96d7-61f051ff44fg",  # TODO 这里可能有权限问题
                    alt="",
                ),
                FeishuMessagePlainText("GitMaya Issue Manual"),
            ),
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
