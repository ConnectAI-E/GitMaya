from .base import *


class RepoManual(FeishuMessageCard):
    def __init__(
        self,
        repo_name="GitMaya",
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_description="待补充",
        visibility="public",
        statuses=["public", "private"],
        archived=False,
    ):
        elements = [
            GitMayaTitle(),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 👀 修改 Repo 可见性**\n*话题下回复「/visit + public, private」*",
                tag="lark_md",
                extra=FeishuMessageSelect(
                    *[
                        FeishuMessageOption(value=status, content=status)
                        for status in statuses
                    ],
                    placeholder="",
                    value={
                        "command": f"/visit ",
                        "suffix": "$option",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="**🥂 修改 Repo 访问权限**\n*话题下回复「/access + read, triger, wirte, maintain, admin + @成员」*",
                tag="lark_md",
            ),
            # repo 标题有问题，先不开放
            # FeishuMessageDiv(
            #     content="** 📑 修改 Repo 标题**\n*话题下回复「/rename + 新 Repo 名称」 *",
            #     tag="lark_md",
            # ),
            FeishuMessageDiv(
                content="**📝 修改 Repo 描述**\n*话题下回复「/edit + 新 Repo 描述」*",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="**⌨️ 修改 Repo 网页**\n*话题下回复「/link + 新 Repo homepage url」*",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="**🏷 添加 Repo 标签**\n*话题下回复「/label + 标签名」*",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content=f"**🕒 更新 Repo 状态**\n*话题下回复「/archive、/unarchive」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    f"{'UnArchive' if archived else 'Archive'} Repo",
                    tag="lark_md",
                    type="primary" if archived else "danger",
                    value={"command": "/unarchive" if archived else "/archive"},
                ),
            ),
            FeishuMessageDiv(
                content=f"**⚡️ 前往 GitHub 查看 Repo 主页 **\n*话题下回复「/view」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "打开 GitHub 主页",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content=f"**📈 前往 GitHub 查看 Repo Insight **\n*话题下回复「/insight」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "打开 Insight 面板",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": f"{repo_url}/pulse",
                        "android_url": f"{repo_url}/pulse",
                        "ios_url": f"{repo_url}/pulse",
                        "pc_url": f"{repo_url}/pulse",
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Repo Manual"),
        ]
        header = FeishuMessageCardHeader("GitMaya Repo Manual\n", template="blue")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


class RepoView(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
    ):
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往 GitHub 查看信息 **",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Repo Action"),
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
    message = RepoManual()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
