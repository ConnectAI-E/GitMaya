import hashlib
import hmac
import os
from functools import wraps
from urllib.parse import parse_qs

import httpx
from app import app
from flask import abort, request


def oauth_by_code(code: str) -> dict | None:
    """Register by code

    Args:
        code (str): The code returned by GitHub OAuth.

    Returns:
        str: The user access token.
    """

    with httpx.Client(
        timeout=httpx.Timeout(10.0, connect=10.0, read=10.0),
        transport=httpx.HTTPTransport(retries=3),
    ) as client:
        response = client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": os.environ.get("GITHUB_CLIENT_ID"),
                "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
                "code": code,
            },
        )
        if response.status_code != 200:
            app.logger.debug(f"Failed to get access token. {response.text}")
            return None

        try:
            oauth_info = parse_qs(response.text)
        except Exception as e:
            app.logger.debug(e)
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
                return func(*args, **kwargs)

            # Verify the signature
            body = request.get_data()

            hash_object = hmac.new(
                secret.encode("utf-8"),
                msg=body,
                digestmod=hashlib.sha256,
            )
            expected_signature = "sha256=" + hash_object.hexdigest()

            app.logger.debug(f"{expected_signature} {signature}")

            if not hmac.compare_digest(expected_signature, signature):
                app.logger.debug("Invalid signature.")
                abort(403, "Invalid signature.")

            return func(*args, **kwargs)

        return wrapper

    return decorator
