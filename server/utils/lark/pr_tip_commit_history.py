from utils.github.model import Commit

from .base import *


class PrTipCommitHistory(FeishuMessageCard):
    def __init__(
        self,
        commits: list[Commit],
    ):
        def process_commit_message(message: str) -> str:
            title = message.split("\n")[0]
            if len(title) > 23:
                title = title[:20] + "..."

        content = "\n".join(
            [
                f"[-@{commit.author.username} - {process_commit_message(commit.message)}]({commit.url})"
                for commit in commits
            ]
        )

        elements = [
            FeishuMessageDiv(
                content=content,
                tag="lark_md",
            ),
            GitMayaCardNote("GitMaya PR Action"),
        ]
        header = FeishuMessageCardHeader("📚 Commit History")
        config = FeishuMessageCardConfig()

        super().__init__(*elements, header=header, config=config)


if __name__ == "__main__":
    import json
    import os

    import httpx
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    message = PrTipCommitHistory()
    print("message", json.dumps(message))
    result = httpx.post(
        os.environ.get("TEST_BOT_HOOK"),
        json={"card": message, "msg_type": "interactive"},
    ).json()
    print("result", result)
