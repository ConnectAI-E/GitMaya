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

        return self.base_github_rest_api(
            f"https://api.github.com/orgs/{org_name}/repos",
            auth_type="install_token",
        )

    def get_org_members(self, org_name: str) -> list | None:
        """Get a list of members of an organization.

        Args:
            org_name (str): The name of the organization.

        Returns:
            list | None: A list of members of the organization.
        https://docs.github.com/zh/rest/orgs/members?apiVersion=2022-11-28#list-organization-members
        """

        return self.base_github_rest_api(
            f"https://api.github.com/orgs/{org_name}/members",
            auth_type="install_token",
        )
