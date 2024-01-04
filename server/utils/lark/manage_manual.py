from base import *


class ManageManual(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repos=[],
        repo_name="GitMaya",
    ):
        new_issue_url = f"{repo_url}/issues/new"
        github_url = "https://github.com"
        setting_url = f"{repo_url}/settings"
        elements = [
            GitMayaTitle(),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 👀 关联历史 Github 项目**\n*话题下回复「/match + repo url + chat name 」 *",
                tag="lark_md",
                extra=FeishuMessageSelect(
                    *[
                        FeishuMessageOption(value=repo, content=name)
                        for name, repo in repos
                    ],
                    placeholder="",
                    value={
                        "key": "value",  # TODO 这里字段的意义需要再看一下，应该是已经选中的人员的openid
                    },
                )
                if len(repos) > 0
                else None,
            ),
            FeishuMessageDiv(
                content="** 📦 新建 Github Repo**\n*话题下回复「/new」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "新建 Github Repo",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": new_issue_url,
                        "android_url": new_issue_url,
                        "ios_url": new_issue_url,
                        "pc_url": new_issue_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content=f"** ⚡️ 查看个人主页 **\n*话题下回复「/view」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "打开 Github 主页",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": github_url,
                        "android_url": github_url,
                        "ios_url": github_url,
                        "pc_url": github_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content=f"** ⚙️ 修改 {repo_name} 设置**\n*话题下回复「/setting 」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "前往 setting 面版",
                    tag="lark_md",
                    type="primary",
                    multi_url={
                        "url": setting_url,
                        "android_url": setting_url,
                        "ios_url": setting_url,
                        "pc_url": setting_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Manage Manual"),
        ]
        header = FeishuMessageCardHeader("GitMaya Manage Manual\n", template="violet")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = ManageManual(repos=[("GitMaya", "GitMaya")])
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
