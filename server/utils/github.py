import os
import time
from urllib.parse import parse_qs

import httpx
from jwt import JWT, jwk_from_pem


def get_jwt(pem_path: str, app_id: str) -> str:
    """Generate a JSON Web Token (JWT) for authentication.

    Args:
        pem_path (str): path to the private key file.
        app_id (str): GitHub App's identifier.

    Returns:
        str: JWT.
    """

    # Open PEM
    with open(pem_path, "rb") as pem_file:
        signing_key = jwk_from_pem(pem_file.read())

    payload = {
        # Issued at time
        "iat": int(time.time()),
        # JWT expiration time (10 minutes maximum)
        "exp": int(time.time()) + 600,
        # GitHub App's identifier
        "iss": app_id,
    }

    # Create JWT
    jwt_instance = JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg="RS256")

    return encoded_jwt


def get_installation_token(jwt: str, installation_id: str) -> str | None:
    """Get installation access token

    Args:
        jwt (str): The JSON Web Token used for authentication.
        installation_id (str): The ID of the installation.

    Returns:
        str: The installation access token.
    """

    with httpx.Client() as client:
        response = client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {jwt}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        if response.status_code == 200:
            return None

        installation_token = response.json().get("token", None)
        return installation_token

    return None


def register_by_code(code: str) -> str | None:
    """Register by code

    Args:
        code (str): The code returned by GitHub OAuth.

    Returns:
        str: The user access token.
    """

    with httpx.Client() as client:
        response = client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": os.environ.get("GITHUB_CLIENT_ID"),
                "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
                "code": code,
            },
        )
        if response.status_code != 200:
            return None

        access_token = parse_qs(response.text).get("access_token", None)
        if access_token is not None:
            return access_token[0]

    return None
