from connectai.lark.sdk import *


class IssueManualHelp(FeishuMessageCard):
    def __init__(
        self,
        repo_url="https://github.com/ConnectAI-E/GitMaya",
        issue_id=16,
        persons=[],
        assignees=[],
    ):
        issue_url = f"{repo_url}/issues/{issue_id}"
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
                        "android_url": "",
                        "ios_url": "",
                        "pc_url": "",
                    },
                ),
            ),
            FeishuMessageHr(),
            FeishuMessageDiv(
                content="** 🕹️ 更新 Issue 状态**\n*话题下回复「/close」/「/reopen」*",
                tag="lark_md",
                extra=FeishuMessageButton(
                    "Close Issue",
                    tag="lark_md",
                    type="danger",
                    multi_url={
                        "url": issue_url,
                        "android_url": "",
                        "ios_url": "",
                        "pc_url": "",
                    },
                ),
            ),
            FeishuMessageDiv(
                content="** 🏖️ 重新分配 Issue 负责人**\n*话题下回复「/assign + @成员」 **",
                tag="lark_md",
                extra=FeishuMessageSelectPerson(
                    *[
                        {
                            "value": person["open_id"],
                        }
                        for person in persons
                    ],
                    placeholder=",".join(assignees),
                    value={
                        "key": "value",  # TODO 这里字段的意义需要再看一下，应该是已经选中的人员的openid
                    },
                ),
            ),
            # TODO
        ]
        header = FeishuMessageCardHeader("ISSUE MANUAL\n", template="gray")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)
