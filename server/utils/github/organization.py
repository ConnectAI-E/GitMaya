from utils.github.bot import BaseGitHubApp


class GitHubAppOrg(BaseGitHubApp):
    def __init__(self, installation_id: str):
        super().__init__(installation_id)

    def get_org_repos(self, org_name: str) -> list | None:
        """Get org repos.

        Args:
            org_name (str): The name of the org.

        Returns:
            list: The org repos.
        https://docs.github.com/zh/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories
        """

        page = 1
        while True:
            repos = self.base_github_rest_api(
                f"https://api.github.com/orgs/{org_name}/repos?page={page}",
                auth_type="install_token",
            )
            if len(repos) == 0:
                break
            for repo in repos:
                yield repo
            page = page + 1

    def get_org_repos_accessible(self) -> list | None:
        """Get accessible org repos.

        Returns:
            list: The accessible org repos.
        https://docs.github.com/zh/rest/apps/installations?apiVersion=2022-11-28#list-repositories-accessible-to-the-app-installation
        """

        page = 1
        while True:
            repos_json = self.base_github_rest_api(
                f"https://api.github.com/installation/repositories?page={page}",
                auth_type="install_token",
            )
            repos = repos_json.get("repositories", [])
            if len(repos) == 0:
                break
            for repo in repos:
                yield repo
            page = page + 1

    def get_org_members(self, org_name: str) -> list | None:
        """Get a list of members of an organization.

        Args:
            org_name (str): The name of the organization.

        Returns:
            list | None: A list of members of the organization.
        https://docs.github.com/zh/rest/orgs/members?apiVersion=2022-11-28#list-organization-members
        """
        page = 1
        while True:
            members = self.base_github_rest_api(
                f"https://api.github.com/orgs/{org_name}/members?page={page}",
                auth_type="install_token",
            )
            if len(members) == 0:
                break
            for member in members:
                yield member
            page = page + 1
