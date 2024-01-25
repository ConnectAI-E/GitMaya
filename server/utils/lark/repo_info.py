from .base import *


class RepoInfo(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_name="GitMaya",
        repo_description="",
        repo_topic=[],
        homepage=None,
        visibility="私有仓库",
        archived=False,
        updated="2022年12月23日 16:32",
        open_issues_count=0,
        stargazers_count=1,
        forks_count=2,
    ):
        labels = (
            "、".join(repo_topic)
            if len(repo_topic) > 0
            else "**<font color='red'>待补充</font>**"
        )
        description = (
            repo_description
            if repo_description is not None
            else "**<font color='red'>待补充</font>**"
        )
        homepage = (
            f"[{homepage}]({homepage})"
            if homepage is not None and homepage != ""
            else "**<font color='red'>待补充</font>**"
        )
        elements = [
            FeishuMessageColumnSet(
                FeishuMessageColumn(
                    FeishuMessageColumnSet(
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**📦 仓库名：** \n{repo_name}",
                                text_align="left",
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
                                f"**🌐 Homepage: **\n{homepage}",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        flex_mode="stretch",
                        background_style="grey",
                    ),
                    FeishuMessageMarkdown(
                        f"**🗒️ 描述：**\n{description}", text_align="left"
                    ),
                    FeishuMessageMarkdown(
                        f"🏷️ **标签：**\n{labels}",
                        text_align="left,",
                    ),
                    width="weighted",
                    weight=1,
                    vertical_align="top",
                ),
                flex_mode="flow",
                background_style="grey",
            ),
            FeishuMessageColumnSet(
                FeishuMessageColumn(
                    FeishuMessageColumnSet(
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**Issue 状态**\n累计 {open_issues_count} 条"
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**Fork 热度**\n累计 {forks_count} 条",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"**Star 热度**\n累计 {stargazers_count} 颗",
                            ),
                            width="auto",
                            weight=1,
                            vertical_align="top",
                        ),
                        flex_mode="stretch",
                        background_style="grey",
                    ),
                ),
                flex_mode="flow",
                background_style="grey",
            ),
            FeishuMessageAction(
                FeishuMessageButton(
                    "新建 Issue",
                    type="primary",
                    multi_url={
                        "url": f"{repo_url}/issues/new",
                        "android_url": f"{repo_url}/issues/new",
                        "ios_url": f"{repo_url}/issues/new",
                        "pc_url": f"{repo_url}/issues/new",
                    },
                ),
                FeishuMessageButton(
                    "打开 Repo Insight",
                    type="plain_text",
                    multi_url={
                        "url": f"{repo_url}/pulse",
                        "android_url": f"{repo_url}/pulse",
                        "ios_url": f"{repo_url}/pulse",
                        "pc_url": f"{repo_url}/pulse",
                    },
                ),
                FeishuMessageButton(
                    "在 GitHub 中打开",
                    type="plain_text",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
                # FeishuMessageOverflow(
                #     FeishuMessageOption(
                #         value="appStore",
                #         content="敬请期待",
                #     ),
                # FeishuMessageOption(
                #     value="appStore",
                #     content="暂停使用项目群",
                # ),
                # FeishuMessageOption(
                #     value="appStore",
                #     content="更新仓库状态",
                # ),
                # ),
            ),
            GitMayaCardNote(f"最近更新 {updated.split('T')[0]}"),
        ]

        header = (
            FeishuMessageCardHeader(
                f"{repo_name} 仓库信息 ** <font color='red'>(已归档)</font> **",
                tag="lark_md",
                template="blue",
            )
            if archived
            else FeishuMessageCardHeader(f"{repo_name} 仓库信息 ", template="blue")
        )

        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = RepoInfo(
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_name="GitMaya",
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
