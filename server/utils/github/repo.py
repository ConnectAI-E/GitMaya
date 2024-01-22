from app import db
from model.schema import CodeApplication, Repo, Team
from utils.github.bot import BaseGitHubApp


class GitHubAppRepo(BaseGitHubApp):
    def __init__(self, installation_id: str = None, user_id: str = None) -> None:
        super().__init__(installation_id=installation_id, user_id=user_id)

    def get_repo_info(self, repo_id: str) -> dict | None:
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

    def get_repo_collaborators(self, repo_name: str, owner_name: str) -> list | None:
        """Get repo collaborators.

        Args:
            repo_name (str): The name of the repo.
            owner_name (str): The name of the owner.

        Returns:
            list: The repo collaborators.
        https://docs.github.com/zh/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators
        """
        page = 1
        while True:
            collaborators = self.base_github_rest_api(
                f"https://api.github.com/repos/{owner_name}/{repo_name}/collaborators?page={page}",
                auth_type="install_token",
            )
            if len(collaborators) == 0:
                break
            for collaborator in collaborators:
                yield collaborator
            page = page + 1

    def update_repo(
        self,
        repo_onwer: str,
        repo_name: str,
        name: str = None,
        description: str = None,
        homepage: str = None,
        private: bool = None,
        visibility: str = None,
        archived: bool = None,
    ) -> dict | None:
        """Update GitHub repo Info

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            name (str): The repo name.
            description (str): The repo description.
            homepage (str): The repo homepage.
            private (bool): The repo private.
            visibility (str): The repo visibility.
            archived (bool): The repo archived.

        Returns:
            dict: The repo info.
        """

        json = dict(
            name=name,
            description=description,
            homepage=homepage,
            private=private,
            visibility=visibility,
            archived=archived,
        )
        json = {k: v for k, v in json.items() if v is not None}

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}",
            "PATCH",
            "user_token",
            json=json,
        )

    def replace_topics(
        self, repo_onwer: str, repo_name: str, topics: list[str]
    ) -> dict | None:
        """Replace topics

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            topics (list[str]): The repo topics.

        Returns:
            dict: The repo info.
        """

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/topics",
            "PUT",
            "user_token",
            json={"names": topics},
        )

    def add_repo_collaborator(
        self,
        repo_onwer: str,
        repo_name: str,
        username: str,
        permission: str = "pull",
    ) -> dict | None:
        """Add repo collaborator

        Note that username should be included in the organization.
        The GitHub API **DO** supports adding a collaborator who
        is not a member of the organization, but here we restrict
        members only.

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            username (str): The username.
            permission (str): The permission. Defaults to "pull".

        Returns:
            dict: The repo info
        """
        res = self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/collaborators/{username}",
            "PUT",
            "user_token",
            json={"permission": permission},
            raw=True,
        )

        if res.status_code == 204:
            return {"status": "success"}
        else:
            return {"status": "failed", "message": res.json()["message"]}

    def create_issue(
        self,
        repo_onwer: str,
        repo_name: str,
        title: str,
        body: str,
        assignees: list[str] = None,
        labels: list[str] = None,
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

    def update_issue(
        self,
        repo_onwer: str,
        repo_name: str,
        issue_number: int,
        title: str = None,
        body: str = None,
        state: str = None,
        state_reason: str = None,
        assignees: list[str] = None,
        labels: list[str] = None,
    ) -> dict | None:
        """Reopen issue

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            issue_number (int): The issue number.

        Returns:
            dict: The issue info.
        """

        json = dict(
            title=title,
            body=body,
            state=state,
            state_reason=state_reason,
            assignees=assignees,
            labels=labels,
        )
        json = {k: v for k, v in json.items() if v is not None}

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/issues/{issue_number}",
            "PATCH",
            "user_token",
            json=json,
        )

    def requested_reviewers(
        self,
        repo_onwer: str,
        repo_name: str,
        pull_number: int,
        reviewers: list[str] = None,
    ):
        """Merge Pull Request
        https://docs.github.com/en/rest/pulls/review-requests?apiVersion=2022-11-28#request-reviewers-for-a-pull-request

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            pull_number (int): The pull number.
            reviewers list[str]: The reviewers.

        Returns:
            dict: The pull request info.
        """
        json = dict(reviewers=reviewers)

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/pulls/{pull_number}/requested_reviewers",
            "POST",
            "user_token",
            json=json,
        )

    def merge_pull_request(
        self,
        repo_onwer: str,
        repo_name: str,
        pull_number: int,
        merge_method: str = "merge",
        commit_title: str = None,
        commit_message: str = None,
    ) -> dict | None:
        """Merge Pull Request

        Args:
            repo_onwer (str): The repo owner.
            repo_name (str): The repo name.
            pull_number (int): The pull number.
            commit_title (str): The comment title.
            commit_message (str): The comment message.
            merge_method (str): The merge method (merge / squash / rebase).

        Returns:
            dict: The merged info.
        """
        json = dict(
            merge_method=merge_method,
            commit_title=commit_title,
            commit_message=commit_message,
        )
        json = {k: v for k, v in json.items() if v is not None}

        return self.base_github_rest_api(
            f"https://api.github.com/repos/{repo_onwer}/{repo_name}/pulls/{pull_number}/merge",
            "PUT",
            "user_token",
            json=json,
        )
