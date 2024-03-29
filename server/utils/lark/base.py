from connectai.lark.sdk import *


class GitMayaTitle(FeishuMessageDiv):
    def __init__(self):
        repo_url = "https://github.com/ConnectAI-E/GitMaya"
        super().__init__(
            content="** 🤠 haloooo，我是 Maya~ **\n对 GitMaya 有新想法? 来 GitHub 贡献你的代码吧。",
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
        )


class GitMayaCardNote(FeishuMessageNote):
    @property
    def img_key(self):
        # TODO 这里似乎应该按机器人生成不同的key，不同租户不同机器人，可能访问的权限是不一样的
        # 已经测试过了，这个跨租户可以使用，可能的原因是，这个是在飞书的卡片构建平台创建的，不是机器人上传的，卡片模板是可以跨租户共享的，所以这个图也能跨租户使用
        return "img_v3_026k_3b6ce6be-4ede-46b0-96d7-61f051ff44fg"

    def __init__(self, content="GitMaya"):
        super().__init__(
            FeishuMessageImage(
                img_key=self.img_key,
                alt="",
            ),
            FeishuMessagePlainText(content),
        )
