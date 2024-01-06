from .base import *


class IssueCard(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        id=16,
        title="",
        description="",
        status="待完成",
        persons=[],
        assignees=[],
        tags=[],
        updated="2022年12月23日 16:32",
    ):
        issue_url = f"{repo_url}/issues/{id}"
        template = "blue" if status == "已关闭" else "red"
        # 这里使用飞书的用户
        # users = " ".join([f"[@{name}]({url})" for name, url in assignees])
        users = "".join(["<at id={open_id}></at>" for open_id in assignees])
        action_button = (
            FeishuMessageButton(
                "重新打开", type="primary", value={"action": f"reopen:{issue_url}"}
            )
            if status == "已关闭"
            else FeishuMessageButton(
                "关闭 Issue", type="danger", value={"action": f"close:{issue_url}"}
            )
        )
        elements = [
            FeishuMessageColumnSet(
                FeishuMessageColumn(
                    FeishuMessageMarkdown(description),
                    FeishuMessageColumnSet(
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"🚧 <font color='grey'>**状态** </font>\n**<font color='{template}'>{status} </font>**",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"👋 <font color='grey'>**分配人**</font>\n{users}",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                f"🏷 <font color='grey'>**标签** </font>\n*{'、'.join(tags)}*",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        flex_mode="bisect",
                        background_style="grey",
                    ),
                    width="weighted",
                    weight=1,
                    vertical_align="top",
                ),
                flex_mode="none",
                background_style="grey",
            ),
            FeishuMessageAction(
                action_button,
                FeishuMessageSelectPerson(
                    *[FeishuMessageOption(value=open_id) for open_id in persons],
                    placeholder="",
                    value={
                        "key": "value",  # TODO 这里字段的意义需要再看一下，应该是已经选中的人员的openid
                    },
                ),
                FeishuMessageButton(
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
            GitMayaCardNote(f"最近更新 {updated}"),
        ]
        header = FeishuMessageCardHeader(f"#Issue{id} {title}", template=template)
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = IssueCard(
        title="优化 OpenAI 默认返回的表格在飞书对话中的呈现",
        description="💬  <font color='black'>**主要内容**</font>\n功能改善建议 🚀\n优化 OpenAI 默认返回的表格在飞书对话中的呈现。\n\n## 您的建议是什么？ 🤔\n\n当前问题1：当要求 OpenAI 使用表格对内容进行格式化返回时，默认会返回 Markdown 格式的文本形式，在飞书对话中显示会很混乱，特别是在手机上查看时。\n\n当前问题2：飞书对话默认不支持 Markdown 语法表格的可视化。\n\n功能预期：返回对话消息如果识别为包含表格内容，支持将内容输出至飞书多维表格，并在对话中返回相应链接。",
        status="待完成",
        # assignees=[("River", "https://github.com/Leizhenpeng")],
        persons=os.environ.get("TEST_USER_OPEN_ID").split(","),
        tags=["bug", "doc"],
        updated="2022年12月23日 16:32",
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
    message = IssueCard(
        title="优化 OpenAI 默认返回的表格在飞书对话中的呈现",
        description="💬  <font color='black'>**主要内容**</font>\n功能改善建议 🚀\n优化 OpenAI 默认返回的表格在飞书对话中的呈现。\n\n## 您的建议是什么？ 🤔\n\n当前问题1：当要求 OpenAI 使用表格对内容进行格式化返回时，默认会返回 Markdown 格式的文本形式，在飞书对话中显示会很混乱，特别是在手机上查看时。\n\n当前问题2：飞书对话默认不支持 Markdown 语法表格的可视化。\n\n功能预期：返回对话消息如果识别为包含表格内容，支持将内容输出至飞书多维表格，并在对话中返回相应链接。",
        status="已关闭",
        # assignees=[("River", "https://github.com/Leizhenpeng")],
        persons=os.environ.get("TEST_USER_OPEN_ID").split(","),
        tags=["bug", "doc"],
        updated="2022年12月23日 16:32",
    )
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
