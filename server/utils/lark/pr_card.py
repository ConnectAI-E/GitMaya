from .base import *


class PullCard(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        id=16,
        title="",
        base=None,
        head=None,
        description="",
        persons=[],
        assignees=[],
        status="待合并",
        labels=[],
        updated="2022年12月23日 16:32",
    ):
        pr_url = f"{repo_url}/pulls/{id}"
        template = "red"
        users = " ".join([f"[@{name}]({url})" for name, url in assignees])
        elements = [
            FeishuMessageColumnSet(
                FeishuMessageColumn(
                    FeishuMessageMarkdown(
                        # TODO 替换content
                        f"🌿  <font color='black'>**分支合并**</font>\n** [{head['ref']}]({repo_url}/tree/{head['ref']}) -> [{base['ref']}]({repo_url}/tree/{base['ref']})",
                        text_align="left",
                    ),
                    FeishuMessageMarkdown(
                        # TODO 替换content
                        description,
                        text_align="left",
                    ),
                    FeishuMessageColumnSet(
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # TODO
                                f"🚧 <font color='grey'>**状态** </font>\n**<font color='Red'>{status} </font>**",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # TODO
                                f"👋 <font color='grey'>**负责人**</font>\n[@River](https://open.feishu.cn/document/ugTN1YjL4UTN24CO1UjN/uUzN1YjL1cTN24SN3UjN?from=mcb)",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # TODO
                                f"👋 <font color='grey'>**审核人**</font>\n[@River](https://open.feishu.cn/document/ugTN1YjL4UTN24CO1UjN/uUzN1YjL1cTN24SN3UjN?from=mcb)、[@Zoe](https://open.feishu.cn/document/ugTN1YjL4UTN24CO1UjN/uUzN1YjL1cTN24SN3UjN?from=mcb)",
                                text_align="left",
                            ),
                            width="weighted",
                            weight=1,
                            vertical_align="top",
                        ),
                        FeishuMessageColumn(
                            FeishuMessageMarkdown(
                                # TODO
                                f"🏷 <font color='grey'>**标签** </font>\n*{labels}*",
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
                FeishuMessageButton(
                    "合并 PR", type="primary", value={"action": f"merge:{pr_url}"}
                ),
                FeishuMessageButton(
                    "关闭 PR", type="danger", value={"action": f"close:{pr_url}"}
                ),
                FeishuMessageButton(
                    "查看 File Changed",
                    type="plain_text",
                    value={"action": f"{pr_url}/files"},
                ),
                FeishuMessageButton(
                    "Commits Log",
                    type="plain_text",
                    value={"action": f"{pr_url}/commits"},
                ),
                FeishuMessageButton(
                    "AI Explain",
                    type="plain_text",
                ),
                FeishuMessageSelectPerson(
                    *[FeishuMessageOption(value=open_id) for open_id in persons],
                    placeholder="修改负责人",
                    value={
                        "key": "value",  # TODO 这里字段的意义需要再看一下，应该是已经选中的人员的openid
                    },
                ),
                FeishuMessageButton(
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
            GitMayaCardNote(f"最近更新 {updated}"),
        ]
        header = FeishuMessageCardHeader(f"#PR{id} {title}", template=template)
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = PullCard(
        title="优化 OpenAI 默认返回的表格在飞书对话中的呈现",
        description="💬  <font color='black'>**主要内容**</font>\n功能改善建议 🚀\n优化 OpenAI 默认返回的表格在飞书对话中的呈现。\n\n## 您的建议是什么？ 🤔\n\n当前问题1：当要求 OpenAI 使用表格对内容进行格式化返回时，默认会返回 Markdown 格式的文本形式，在飞书对话中显示会很混乱，特别是在手机上查看时。\n\n当前问题2：飞书对话默认不支持 Markdown 语法表格的可视化。\n\n功能预期：返回对话消息如果识别为包含表格内容，支持将内容输出至飞书多维表格，并在对话中返回相应链接。",
        assignees=[("River", "https://github.com/Leizhenpeng")],
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
