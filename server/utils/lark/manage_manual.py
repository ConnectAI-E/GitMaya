import os

from .base import *


class ManageManual(FeishuMessageCard):
    def __init__(
        self,
        org_name="GitMaya",
        repos=[],
        team_id="",
    ):
        github_url = "https://github.com"
        new_repo_url = f"{github_url}/new"
        profile_url = f"{github_url}/{org_name}"
        gitmaya_host = os.environ.get("DOMAIN")
        setting_url = f"{gitmaya_host}/app/setting"
        elements = [
            GitMayaTitle(),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 👀 关联历史 GitHub 项目**\n*回复「/match + repo url + chat name 」 *",
                tag="lark_md",
                extra=FeishuMessageSelect(
                    *[
                        FeishuMessageOption(value=repo_name, content=repo_name)
                        for _, repo_name in repos
                    ],
                    placeholder="",
                    value={
                        # /match_repo_id + select repo_id, with chat_id
                        # 这里直接使用前面选中的项目名字拼接到github_url后面，就与用户输入match指令一致了
                        "command": f"/match {github_url}/{org_name}/",
                        "suffix": "$option",
                    },
                )
                if len(repos) > 0
                else None,
            ),
            FeishuMessageDiv(
                content="** 📦 新建 GitHub Repo**\n*回复「/new」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "新建 GitHub Repo",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": new_repo_url,
                        "android_url": new_repo_url,
                        "ios_url": new_repo_url,
                        "pc_url": new_repo_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content=f"** ⚡️ 查看个人主页 **\n*回复「/view」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "打开 GitHub 主页",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": profile_url,
                        "android_url": profile_url,
                        "ios_url": profile_url,
                        "pc_url": profile_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content=f"** ⚙️ 修改 {org_name} 设置**\n*回复「/setting 」*",
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


class ManageView(FeishuMessageCard):
    def __init__(self, org_name="GitMaya"):
        github_url = "https://github.com"
        profile_url = f"{github_url}/{org_name}"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 GitHub 查看个人主页 **",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": profile_url,
                        "android_url": profile_url,
                        "ios_url": profile_url,
                        "pc_url": profile_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Manage Action"),
        ]
        header = FeishuMessageCardHeader("🎉 操作成功！")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


class ManageNew(FeishuMessageCard):
    def __init__(self):
        github_url = "https://github.com"
        new_repo_url = f"{github_url}/new"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 GitHub 新建 Repo **",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": new_repo_url,
                        "android_url": new_repo_url,
                        "ios_url": new_repo_url,
                        "pc_url": new_repo_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Manage Action"),
        ]
        header = FeishuMessageCardHeader("🎉 操作成功！")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


class ManageSetting(FeishuMessageCard):
    def __init__(self):
        gitmaya_host = os.environ.get("DOMAIN")
        setting_url = f"{gitmaya_host}/app/setting"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 GitHub 查看 **",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": setting_url,
                        "android_url": setting_url,
                        "ios_url": setting_url,
                        "pc_url": setting_url,
                    },
                ),
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
    message = ManageManual(repos=[("GitMaya", "GitMaya")])
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
