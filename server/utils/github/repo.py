from utils.github.bot import BaseGitHubApp


class GitHubAppRepo(BaseGitHubApp):
    def __init__(self, installation_id: str = None) -> None:
        super().__init__(installation_id=installation_id)

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
