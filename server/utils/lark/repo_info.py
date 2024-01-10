from .base import *


class RepoInfo(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        repo_name="GitMaya",
        repo_description="aaaaaaaaaa",
        repo_topic=["aaa", "ccc"],
        homepage="",
        visibility="私有仓库",
        updated="2022年12月23日 16:32",
        open_issues_count=0,
        stargazers_count=1,
        forks_count=2,
    ):
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
                                f"**🌐 Homepage：**\n{homepage}",
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
                        f"**🗒️ 描述：**\n{repo_description}\n\n", text_align="left"
                    ),
                    FeishuMessageMarkdown(
                        f"**🏷️ Topic**：\n{'、'.join(repo_topic)}", text_align="left"
                    ),
                    width="auto",
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
                                # f"**Issue 状态**\n<font color='green'>待处理 {issue_need_process_num} 条</font>\n累计 {issue_total_num} 条"
                                f"**Issue 状态**\n累计 {open_issues_count} 条"
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        # FeishuMessageColumn(
                        #     FeishuMessageMarkdown(
                        #         f"**Pr 状态**\n<font color='green'>待合并 {pr_need_process_num} 条</font>\n累计 {pr_total_num} 条",
                        #     ),
                        #     width="weighted",
                        #     weight=1,
                        #     vertical_align="top",
                        # ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # f"**Fork 热度**\n<font color='green'>本周新增 {fork_new_num} 条</font>\n累计 {fork_total_num} 条",
                                f"**Fork 热度**\n累计 {forks_count} 条",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # f"**Star 热度**\n<font color='green'>本周新增 {star_new_num} 条</font>\n累计 {star_total_num} 条",
                                f"**Star 热度**\n累计 {stargazers_count} 条",
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
                    type="default",
                    multi_url={
                        "url": f"{repo_url}/pulse",
                        "android_url": f"{repo_url}/pulse",
                        "ios_url": f"{repo_url}/pulse",
                        "pc_url": f"{repo_url}/pulse",
                    },
                ),
                FeishuMessageButton(
                    "在 GitHub 中打开",
                    type="default",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
                FeishuMessageButton(
                    "···",
                    type="default",
                    multi_url={
                        "url": repo_url,
                        "android_url": repo_url,
                        "ios_url": repo_url,
                        "pc_url": repo_url,
                    },
                ),
            ),
            GitMayaCardNote(f"最近更新 {updated.split('T')[0]}"),
        ]
        header = FeishuMessageCardHeader(f"{repo_name} 仓库信息", template="blue")
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
        repo_description="🖲️ Next generation gitops for boosting developer-teams productivity",
        repo_topic=["GitMaya", "git", "feishu", "lark"],
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
