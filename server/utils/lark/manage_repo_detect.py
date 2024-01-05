from .base import *


class ManageRepoDetect(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_name="GitMaya",
        repo_description="",
        repo_topic=[],
        visibility="私有仓库",
    ):
        new_issue_url = f"{repo_url}/issues/new"
        github_url = "https://github.com"
        setting_url = f"{repo_url}/settings"
        elements = [
            FeishuMessageColumnSet(
                FeishuMessageColumn(
                    FeishuMessageColumnSet(
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**📦 仓库名：** \n{repo_name}\n",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**👀 可见性：**\n{visibility}",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**🌐 Homepage：**\n{repo_url}",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        flex_mode="stretch",
                        background_style="grey",
                    ),
                    width="auto",
                    weight=1,
                    vertical_align="top",
                ),
                FeishuMessageMarkdown(f"**🗒️ 描述：**\n{repo_description}", text_align="left),
                FeishuMessageMarkdown(f"**🏷️ Topic**：\n{'、'.join(repo_topic)}", text_align="left),
                flex_mode="flow",
                background_style="grey",
            ),
            FeishuMessageAction(
                FeishuMessageButton(
                    "创建项目群",
                    type="primary",
                    value={"action": "create:chat_group"},
                ),
                FeishuMessageButton(
                    "在浏览器中打开",
                    type="default",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
                FeishuMessageOverflow(FeishuMessageOption(value="appStore", content="关联已有项目群")),
            ),
            GitMayaCardNote("GitMaya Manage Action"),
        ]
        header = FeishuMessageCardHeader("发现了新的 GitHub 仓库", template="violet")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = ManageRepoDetect(
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_name="GitMaya",
        repo_description="🖲️ Next generation gitops for boosting developer-teams productivity",
        repo_topic=["GitMaya", "git", "feishu", "lark"],
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
