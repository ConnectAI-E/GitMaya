from app import db
from model.schema import CodeApplication, Repo, Team
from utils.github.bot import BaseGitHubApp


class GitHubAppRepo(BaseGitHubApp):
    def __init__(self, installation_id: str = None, user_id: str = None) -> None:
        super().__init__(installation_id=installation_id, user_id=user_id)

    def get_repo_info(self, repo_id) -> dict | None:
        """Get repo info by repo ID.

        Args:
            repo_id (str): The repo ID from GitHub.

        Returns:
            dict: Repo info.
        """
        # 检查 repo 是否存在，是否属于当前 app，如果不存在，返回 None
        # 注意：这里的 repo_id 是 GitHub 的 repo_id，不是数据库中 id
        repo = Repo.query.filter_by(repo_id=repo_id).first()
        if not repo:
            return None

        team = (
            db.session.query(Team)
            .join(
                CodeApplication,
                CodeApplication.team_id == Team.id,
            )
            .filter(
                CodeApplication.id == repo.application_id,
            )
            .first()
        )
        if not team:
            return None

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{team.name}/{repo.name}",
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
