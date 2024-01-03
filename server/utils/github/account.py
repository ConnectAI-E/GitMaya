import httpx
from app import app


def get_user_info(access_token: str) -> dict | None:
    """Get user info by access token.

    Args:
        access_token (str): The user access token.

    Returns:
        dict: User info.
    """

    with httpx.Client() as client:
        response = client.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {access_token}",
            },
        )
        if response.status_code != 200:
            app.logger.debug(f"Failed to get user info. {response.text}")
            return None

        user_info = response.json()
        return user_info

    app.logger.debug("Failed to get user info.")
    return None


def get_email(access_token: str) -> str | None:
    """Get user email by access token.

    Args:
        access_token (str): The user access token.

    Returns:
        str: User email.
    """

    with httpx.Client() as client:
        response = client.get(
            "https://api.github.com/user/emails",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        if response.status_code != 200:
            app.logger.debug(f"Failed to get user email. {response.text}")
            return None

        user_emails = response.json()
        if len(user_emails) == 0:
            app.logger.debug("Failed to get user email.")
            return None

        for user_email in user_emails:
            if user_email["primary"]:
                return user_email["email"]

        return user_emails[0]["email"]

    app.logger.debug("Failed to get user email.")
    return None
