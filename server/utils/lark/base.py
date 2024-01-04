from connectai.lark.sdk import *


class GitMayaCardNote(FeishuMessageNote):
    def __init__(self, content="GitMaya"):
        super().__init__(
            FeishuMessageImage(
                img_key="img_v3_026k_3b6ce6be-4ede-46b0-96d7-61f051ff44fg",  # TODO 这里可能有权限问题
                alt="",
            ),
            FeishuMessagePlainText(content),
        )
