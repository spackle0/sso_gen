# coding=utf-8
"""
SSO Classes
"""

# Standard Library
import glob
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Third Party Libraries
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, ParamValidationError
from dateutil import parser

# Custom Libraries
from . import config
from .custom_exceptions import (CantAccessAccount, CommandError,
                                       NeedNewToken)

CACHE_DIR = config.files["cache_dir"]


# Classes


class SsoClient:
    """
    SSO work
    """

    __slots__ = "access_token", "cache_dir", "client", "sso_profile", "account_list"

    def __init__(self, sso_profile, cache_dir=CACHE_DIR):
        client_config = Config(region_name="us-east-1")
        self.client = boto3.client("sso", config=client_config)
        self.sso_profile = sso_profile
        self.cache_dir = cache_dir
        try:
            (self.access_token, self.account_list) = self.get_access_token()
        except CommandError as error:
            print(f"Error getting access token: {error}")
            sys.exit(1)

    def get_cached_sso_token(
        self,
    ) -> str:  # pylint: disable=inconsistent-return-statements
        """Grab the SSO token from the cache. If it's expired, ask the user
        to SSO login"""
        keys = {"startUrl", "accessToken", "expiresAt"}
        for file in glob.glob(os.path.join(self.cache_dir, "*.json")):
            with open(file, mode="r", encoding="utf-8") as json_file:
                content = json.load(json_file)
            # If we have at least the above keys, and the token isn't expired, then
            # we have a current token
            if content.keys() >= keys and SsoClient.unexpired(content["expiresAt"]):
                print("Found an unexpired access token.")
                self.access_token = content["accessToken"]
                return self.access_token

        # We didn't find a cached token, or it was expired
        raise NeedNewToken

    def get_account_list(self) -> dict:
        """Get the list of accounts available to this user based upon the sso login"""

        response = self.client.list_accounts(
            accessToken=self.access_token, maxResults=50
        )
        return response["accountList"]

    def get_access_token(self) -> tuple:
        """
        Try the cached access token (if it exists), otherwise get a new one and test
        that it works
        """
        count = 0

        while True:
            try:
                self.access_token = self.get_cached_sso_token()
                return self.access_token, self.get_account_list()

            except (ParamValidationError, ClientError) as sso_error:
                raise RuntimeError(f"API error: {sso_error}") from sso_error

            except NeedNewToken as sso_error:
                # We have an invalid token
                if count >= config.MAX_SSO_RETRIES:
                    raise RuntimeError(
                        "Unable to obtain a new SSO Access Token."
                    ) from sso_error

                count += 1
                return_code = SsoClient.sso_login(self.sso_profile)
                if return_code != 0:
                    raise CommandError("sso login command had an error") from sso_error
                continue

    def get_role_list(self, account_id):
        """Get the roles associated with the user in the account"""
        response = self.client.list_account_roles(
            accessToken=self.access_token, accountId=account_id
        )
        return response["roleList"]

    def get_role_creds(self, acct, role) -> dict:
        """Get the temp STS creds for the role/acct"""
        response = {}
        try:
            response = self.client.get_role_credentials(
                roleName=role, accountId=acct, accessToken=self.access_token
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ForbiddenException":
                raise CantAccessAccount from error
        return response["roleCredentials"]

    @staticmethod
    def unexpired(expiration: str) -> bool:
        """Parse whatever date format the token expiration is stored in and"""
        expiration_date = parser.parse(expiration)
        return expiration_date > datetime.now(timezone.utc)

    # TODO: Confirm whether "shell=True" is needed
    @staticmethod
    def sso_login(sso_profile: str) -> int:
        """
        2021-09-16
        We have an expired or nonexistent sso token, so we need to generate one. As of
        the writing of this, boto3 does not have a mechanism to do "aws sso login" so
        we must use the shell. In addition, there is no way around the need to log in
        to sso via a browser window. There may be a way to do this with OIDC, but it's
        a project for the future.
        """
        with subprocess.Popen(
            [f"aws sso login --profile {sso_profile}"],
            shell=True,
            stdout=subprocess.PIPE,
        ) as process:
            while True:
                output = process.stdout.readline().strip().decode("utf-8")
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output)
            return_code = process.poll()

        return return_code
