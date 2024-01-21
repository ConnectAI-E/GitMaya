import logging
import os
import time
from datetime import datetime

import httpx
from jwt import JWT, jwk_from_pem
from model.schema import BindUser
from utils.constant import GitHubPermissionError


class BaseGitHubApp:
    def __init__(self, installation_id: str = None, user_id: str = None) -> None:
        self.app_id = os.environ.get("GITHUB_APP_ID")
        self.client_id = os.environ.get("GITHUB_CLIENT_ID")
        self.installation_id = installation_id
        self.user_id = user_id

        self._jwt_created_at: float = None
        self._jwt: str = None

        self._installation_token_created_at: float = None
        self._installation_token: str = None

        self._user_token_created_at: float = None
        self._user_token: str = None

    def base_github_rest_api(
        self,
        url: str,
        method: str = "GET",
        auth_type: str = "jwt",
        json: dict = None,
        raw: bool = False,
    ) -> dict | list | httpx.Response | None:
        """Base GitHub REST API.

        Args:
            url (str): The url of the GitHub REST API.
            method (str, optional): The method of the GitHub REST API. Defaults to "GET".
            auth_type (str, optional): The type of the authentication. Defaults to "jwt", can be "jwt" or "install_token" or "user_token".

        Returns:
            dict | list | None: The response of the GitHub REST API.
        """

        auth = ""

        match auth_type:
            case "jwt":
                auth = self.jwt
            case "install_token":
                auth = self.installation_token
            case "user_token":
                auth = self.user_token
            case _:
                raise ValueError(
                    "auth_type must be 'jwt' or 'install_token' or 'user_token'"
                )

        with httpx.Client(
            timeout=httpx.Timeout(10.0, connect=10.0, read=10.0),
            transport=httpx.HTTPTransport(retries=3),
        ) as client:
            response = client.request(
                method,
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {auth}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json=json,
            )
            if response.status_code == 401:
                logging.error("base_github_rest_api: GitHub Permission Error")
                raise GitHubPermissionError(response.json().get("message"))
            if raw:
                return response
            return response.json()

    @property
    def jwt(self) -> str:
        """Get a JWT for the GitHub App.

        Returns:
            str: A JWT for the GitHub App.
        """
        # 判断是否初始化了 jwt，或者 jwt 是否过期
        if (
            self._jwt is None
            or self._jwt_created_at is None
            or datetime.now().timestamp() - self._jwt_created_at > 60 * 10
        ):
            self._jwt_created_at = datetime.now().timestamp()

            if os.environ.get("GITHUB_APP_PRIVATE_KEY"):
                signing_key = jwk_from_pem(
                    os.environ.get("GITHUB_APP_PRIVATE_KEY").encode()
                )
            else:
                with open(
                    os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH", "pem.pem"), "rb"
                ) as pem_file:
                    signing_key = jwk_from_pem(pem_file.read())

            payload = {
                # Issued at time
                "iat": int(time.time()),
                # JWT expiration time (10 minutes maximum)
                "exp": int(time.time()) + 600,
                # GitHub App's identifier
                "iss": self.app_id,
            }

            # Create JWT
            jwt_instance = JWT()
            self._jwt = jwt_instance.encode(payload, signing_key, alg="RS256")

        return self._jwt

    @property
    def installation_token(self) -> str:
        """Get an installation token for the GitHub App.

        Returns:
            str: An installation token for the GitHub App.
        """
        if (
            self._installation_token is None
            or self._installation_token_created_at is None
            or datetime.now().timestamp() - self._installation_token_created_at
            > 60 * 60
        ):
            res = self.base_github_rest_api(
                f"https://api.github.com/app/installations/{self.installation_id}/access_tokens",
                method="POST",
            )

            self._installation_token_created_at = datetime.now().timestamp()
            self._installation_token = res.get("token", None)

        return self._installation_token

    @property
    def user_token(self) -> str:
        """Get a user token for the GitHub App.

        Returns:
            str: A user token for the GitHub App.
        """

        # TODO: 当前使用的是无期限的 token，可能需要考虑刷新 token 的问题
        if (self._user_token is None or self._user_token_created_at is None,):
            bind_user = BindUser.query.filter_by(
                user_id=self.user_id, platform="github"
            ).first()
            if bind_user is None:
                raise Exception("Failed to get bind user.")

            if bind_user.access_token is None:
                # 这种情况下可能是用户没有绑定 GitHub
                raise Exception("Failed to get access token.")

            self._user_token_created_at = datetime.now().timestamp()
            self._user_token = bind_user.access_token

        return self._user_token

    def get_installation_info(self) -> dict | None:
        """Get installation info

        Returns:
            dict: The installation info.
        https://docs.github.com/zh/rest/apps/apps?apiVersion=2022-11-28#get-an-installation-for-the-authenticated-app
        """

        return self.base_github_rest_api(
            f"https://api.github.com/app/installations/{self.installation_id}"
        )
