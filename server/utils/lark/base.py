from connectai.lark.sdk import *


class GitMayaCardNote(FeishuMessageNote):
    @property
    def img_key(self):
        # TODO 这里似乎应该按机器人生成不同的key，不同租户不同机器人，可能访问的权限是不一样的
        return "img_v3_026k_3b6ce6be-4ede-46b0-96d7-61f051ff44fg"

    def __init__(self, content="GitMaya"):
        super().__init__(
            FeishuMessageImage(
                img_key=self.img_key,
                alt="",
            ),
            FeishuMessagePlainText(content),
        )
