from utils.github.bot import BaseGitHubApp


class GitHubAppRepo(BaseGitHubApp):
    def __init__(self, installation_id: str = None, user_id: str = None) -> None:
        super().__init__(installation_id=installation_id, user_id=user_id)

    def get_repo(self, repo_onwer: str, repo_name: str) -> dict | None:
        """Get repo

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.

        Returns:
            dict: The repo info.
        """

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}",
            "GET",
            "install_token",
        )

    def create_issue(
        self,
        repo_onwer: str,
        repo_name: str,
        title: str,
        body: str,
        assignees: list[str],
        labels: list[str],
    ) -> dict | None:
        """Create issue

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            title (str): The issue title.
            body (str): The issue body.
            assignees (list[str]): The issue assignees.
            labels (list[str]): The issue labels.

        Returns:
            dict: The issue info.
        """

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/issues",
            "POST",
            "user_token",
            json={
                "title": title,
                "body": body,
                "assignees": assignees,
                "labels": labels,
            },
        )

    def create_issue_comment(
        self, repo_onwer: str, repo_name: str, issue_number: int, body: str
    ) -> dict | None:
        """Create issue comment

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            issue_number (int): The issue number.
            body (str): The comment body.

        Returns:
            dict: The comment info.
        """

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/issues/{issue_number}/comments",
            "POST",
            "user_token",
            json={"body": body},
        )
