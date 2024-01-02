import hashlib
import hmac
import logging
import os
import time
from functools import wraps
from urllib.parse import parse_qs

import httpx
from flask import abort, request
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
        if response.status_code != 200:
            logging.debug(f"Failed to get installation token. {response.text}")
            return None

        installation_token = response.json().get("token", None)
        return installation_token

    return None


def oauth_by_code(code: str) -> dict | None:
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

        try:
            oauth_info = parse_qs(response.text)
        except Exception as e:
            logging.debug(e)
            return None

    return oauth_info


def verify_github_signature(
    secret: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "secret")
):
    """Decorator to verify the signature of a GitHub webhook request.

    Args:
        secret (str): The secret key used to sign the webhook request.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            signature = request.headers.get("x-hub-signature-256")
            if not signature:
                abort(400, "No signature provided.")

            # Verify the signature
            body = request.get_data()

            hash_object = hmac.new(
                secret.encode("utf-8"),
                msg=body,
                digestmod=hashlib.sha256,
            )
            expected_signature = "sha256=" + hash_object.hexdigest()

            logging.debug(f"{expected_signature} {signature}")

            if not hmac.compare_digest(expected_signature, signature):
                logging.debug("Invalid signature.")
                abort(403, "Invalid signature.")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_user_info(access_token: str):
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
            logging.debug(f"Failed to get user info. {response.text}")
            return None

        user_info = response.json()
        return user_info

    return None
