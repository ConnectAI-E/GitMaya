import httpx
from app import app


def get_org_members(org_name: str, installation_token: str) -> list | None:
    """Get a list of members of an organization.

    Args:
        org_name (str): The name of the organization.
        installation_token (str): The installation token for the GitHub App.

    Returns:
        list | None: A list of members of the organization.
    https://docs.github.com/zh/rest/orgs/members?apiVersion=2022-11-28#list-organization-members
    """
    with httpx.Client() as client:
        response = client.get(
            f"https://api.github.com/orgs/{org_name}/members",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            app.logger.debug(f"Failed to get org members. {response.text}")
            return None
