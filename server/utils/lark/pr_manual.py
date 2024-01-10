from .base import *


class PrManual(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        pr_id=17,
        persons=[],
        assignees=[],
        tags=[],
        merged=False,
    ):
        pr_url = f"{repo_url}/pull/{pr_id}"
        elements = [
            FeishuMessageDiv(
                content="** 🤠 haloooo，我是Maya~ **\n对 GitMaya 有新想法? 来Github 贡献你的代码吧。",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "⭐️ Star Maya",
                    tag="lark_md",
                    type="primary",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
            ),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 🕹️ 更新 Pr 状态**\n*话题下回复「 /merge, /close, /reopen」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "Merge PR",
                    tag="lark_md",
                    type="primary",
                    value={
                        "command": f"/merge ",
                    },
                )
                if not merged
                else None,
            ),
            FeishuMessageDiv(
                content="** 🕹️ 查看 Commits Log**\n*话题下回复「 /log 」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "查看 Commits Log",
                    tag="lark_md",
                    type="primary",
                    multi_url={
                        "url": f"{pr_url}/commits",
                        "android_url": f"{pr_url}/commits",
                        "ios_url": f"{pr_url}/commits",
                        "pc_url": f"{pr_url}/commits",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🔄 查看 File Changed**\n*话题下回复「 /diff 」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "查看 File changed",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": f"{pr_url}/files",
                        "android_url": f"{pr_url}/files",
                        "ios_url": f"{pr_url}/files",
                        "pc_url": f"{pr_url}/files",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🔥 AI Summary **\n*话题下回复「 /summary 」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "Run",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": pr_url,
                        "android_url": pr_url,
                        "ios_url": pr_url,
                        "pc_url": pr_url,
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🏖️ 重新分配 Pr 负责人**\n*话题下回复「/assign + @成员」 *",
                tag="lark_md",
                extra=FeishuMessageSelectPerson(
                    *[FeishuMessageOption(value=open_id) for open_id in persons],
                    placeholder="",
                    value={
                        "command": f"/assign ",
                        "suffix": "$option",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🏷️  修改 Pr 标签**\n*话题下回复「/label + 标签名」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** 📑 修改 Pr 标题**\n*话题下回复「 /rename + 新 Pr 标题 」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** 📝 编辑 Pr 描述**\n*话题下回复「 /edit + 另起一行 + 新 pr 描述 」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** ⌨️ 在 Pr 下评论**\n*话题下直接回复「 你的评论」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** ⚡️ 查看更多 Pr 信息 **\n*话题下回复「 /view 」 *",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器中打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": pr_url,
                        "android_url": pr_url,
                        "ios_url": pr_url,
                        "pc_url": pr_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Pr Manual"),
        ]
        header = FeishuMessageCardHeader("PR MANUAL\n", template="grey")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os
    from pprint import pprint

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = PrManual(
        pr_id=17,
        persons=os.environ.get("TEST_USER_OPEN_ID").split(","),
        tags=["bug", "doc"],
    )
    pprint(json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    pprint(result)
