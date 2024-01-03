import httpx

from server import app


def get_org_repos(org_name: str, installation_token: str) -> list | None:
    """Get org repos.

    Args:
        org_name (str): The name of the org.
        installation_token (str): The installation access token.

    Returns:
        list: The org repos.
    https://docs.github.com/zh/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories
    """
    with httpx.Client() as client:
        response = client.get(
            f"https://api.github.com/orgs/{org_name}/repos",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            app.logger.debug(f"Failed to get org repos. {response.text}")
            return None


def get_repo_collaborators(
    repo_name: str, owner_name: str, installation_token: str
) -> list | None:
    """Get repo collaborators.

    Args:
        repo_name (str): The name of the repo.
        owner_name (str): The name of the owner.
        installation_token (str): The installation access token.

    Returns:
        list: The repo collaborators.
    https://docs.github.com/zh/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators
    """

    with httpx.Client() as client:
        response = client.get(
            f"https://api.github.com/repos/{owner_name}/{repo_name}/collaborators",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            app.logger.debug(f"Failed to get repo collaborators. {response.text}")
            return None
