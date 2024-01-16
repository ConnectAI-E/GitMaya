from .base import *


class IssueManualHelp(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        issue_id=16,
        persons=[],
        assignees=[],
        status="待完成",
        tags=[],
    ):
        issue_url = f"{repo_url}/issues/{issue_id}"
        action_button = (
            FeishuMessageButton("重新打开", type="primary", value={"command": f"/reopen"})
            if status == "已关闭"
            else FeishuMessageButton(
                "关闭 Issue", type="danger", value={"command": f"/close"}
            )
        )
        elements = [
            GitMayaTitle(),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 🕹️ 更新 Issue 状态**\n*话题下回复「/close、/reopen」*",
                tag="lark_md",
                extra=action_button,
            ),
            FeishuMessageDiv(
                content="** 🏖️ 重新分配 Issue 负责人**\n*话题下回复「/assign + @成员」*",
                tag="lark_md",
                extra=FeishuMessageSelectPerson(
                    # *[FeishuMessageOption(value=open_id) for open_id in persons],
                    placeholder="修改负责人",
                    value={
                        "command": "/assign ",
                        "suffix": "$option",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🏷️  修改 Issue 标签**\n*话题下回复「/label + 标签名」 *",
                tag="lark_md",
                extra=FeishuMessageSelect(
                    *[FeishuMessageOption(value=tag) for tag in tags],
                    placeholder="修改标签",
                    value={
                        "command": "/label ",
                        "suffix": "$option",
                    },
                )
                if len(tags)
                else None,
            ),
            # FeishuMessageDiv(
            #     content="** 🔝 置顶 Issue**\n*话题下回复「/pin、/unpin」 *",
            #     tag="lark_md",
            #     extra=FeishuMessageButton(
            #         "Pin Issue",
            #         tag="lark_md",
            #         type="primary",
            #         multi_url={
            #             "url": issue_url,
            #             "android_url": issue_url,
            #             "ios_url": issue_url,
            #             "pc_url": issue_url,
            #         },
            #     ),
            # ),
            FeishuMessageDiv(
                content="** 📑 修改 Issue 标题**\n*话题下回复「/rename + 新 Issue 标题」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** 📝 编辑 Issue 描述**\n*话题下回复「/edit + 另起一行 + 新 Issue 描述」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** ⌨️ 在 Issue 下评论**\n*话题下回复「 你的评论」 *",
                tag="lark_md",
            ),
            FeishuMessageDiv(
                content="** ⚡️ 查看更多 Issue 信息 **\n*话题下回复「/view」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器中打开",
                    tag="lark_md",
                    type="default",
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
        header = FeishuMessageCardHeader("ISSUE MANUAL\n", template="grey")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


class IssueView(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        issue_id=17,
    ):
        issue_url = f"{repo_url}/issues/{issue_id}"
        elements = [
            FeishuMessageDiv(
                content=f"** ⚡️ 前往GitHub查看信息 **",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "在浏览器打开",
                    tag="lark_md",
                    type="default",
                    multi_url={
                        "url": issue_url,
                        "android_url": issue_url,
                        "ios_url": issue_url,
                        "pc_url": issue_url,
                    },
                ),
            ),
            GitMayaCardNote("GitMaya Issue Action"),
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
    message = IssueManualHelp(
        persons=os.environ.get("TEST_USER_OPEN_ID").split(","), tags=["bug", "doc"]
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
