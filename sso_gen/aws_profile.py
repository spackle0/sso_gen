# coding=utf-8
"""
Class for manipulating AWS configuration and credentials files
"""

# Standard Library
import configparser

from . import config, sso
from .config import logger
from .custom_exceptions import CantAccessAccount

CONFIG_FILE = config.files["config_file"]
CREDENTIALS_FILE = config.files["credentials_file"]
ORG_PREFIX = config.aws["org_prefix"]
DEFAULT_PROFILE = config.DEFAULT_PROFILE


# TODO: Break this up, SRP of SOLID
class AwsProfiles:
    """
    Manipulates AWS config and credentials.
    """

    __slots__ = "config_file", "credentials_file", "sso_profile", "sso_client"

    def __init__(
        self,
        config_file=CONFIG_FILE,
        credentials_file=CREDENTIALS_FILE,
    ):
        self.config_file = {
            "content": AwsProfiles.get_aws_file(config_file),
            "path": config_file,
        }
        self.credentials_file = {
            "content": AwsProfiles.get_aws_file(credentials_file),
            "path": credentials_file,
        }
        self.sso_profile = AwsProfiles.check_default_profile(
            self.config_file["content"], DEFAULT_PROFILE
        )

        self.sso_client = sso.SsoClient(self.sso_profile)

    @staticmethod
    def get_aws_file(file_path) -> configparser.RawConfigParser:
        """Read the AWS credentials file"""
        file_content = configparser.ConfigParser()
        file_content.read(file_path)
        return file_content

    def update_credential(self, profile_name, creds):
        """Update the relevant profile section with the STS credentials"""
        # If the credentials file doesn't have the section yet, add it
        credentials_file = self.credentials_file["content"]
        if not credentials_file.has_section(profile_name):
            credentials_file.add_section(profile_name)

        credentials_file[profile_name]["access_key_id"] = creds["accessKeyId"]
        credentials_file[profile_name]["secret_access_key"] = creds["secretAccessKey"]
        credentials_file[profile_name]["session_token"] = creds["sessionToken"]

    def update_config(self, config_profile, account_id, role):
        """Add or modify a profile in the aws config"""
        current_config = self.config_file["content"]
        if not current_config.has_section(config_profile):
            current_config.add_section(config_profile)

        current_config[config_profile]["sso_start_url"] = config.aws["sso_start_url"]
        current_config[config_profile]["sso_region"] = "us-east-1"
        current_config[config_profile]["sso_account_id"] = account_id
        current_config[config_profile]["sso_role_name"] = role

    def process_credentials(self):
        """
        Loop through accounts and get credentials for each role the user has in
        that account
        """

        logger.info("Getting credentials for:")
        for account in self.sso_client.account_list:
            account_id = account["accountId"]
            for role_info in self.sso_client.get_role_list(account_id):
                role_name = role_info["roleName"]
                try:
                    creds_profile = (
                        f"{ORG_PREFIX}-"
                        f'{config.aws["account_map"][account_id]}-'
                        f"{role_name}"
                    )
                except KeyError as err:
                    logger.error(
                        "Can't get map for account %s. New account? SKIPPING: %s",
                        account_id,
                        err,
                    )
                    continue
                config_profile = f"profile {creds_profile}"
                logger.info('Created "%s"', creds_profile)

                try:
                    creds = self.sso_client.get_role_creds(account_id, role_name)
                except CantAccessAccount as error:
                    logger.error("Unable to access account %s: %s", account, error)
                    continue

                self.update_config(config_profile, account_id, role_name)
                self.update_credential(creds_profile, creds)

    def write_files(self):
        """Save files to disk"""
        (current_config, config_file) = (
            self.config_file["content"],
            self.config_file["path"],
        )

        (current_credentials, credentials_file) = (
            self.credentials_file["content"],
            self.credentials_file["path"],
        )

        logger.info('Writing "%s"', credentials_file)
        with open(
            self.credentials_file["path"], mode="w", encoding="utf-8"
        ) as credentials_file_fp:
            current_credentials.write(credentials_file_fp)

        logger.info('Writing "%s"', config_file)
        with open(CONFIG_FILE, mode="w", encoding="utf-8") as config_file_fp:
            current_config.write(config_file_fp)

    @staticmethod
    def check_default_profile(content, default_profile: str):
        """
        Check for the default profile TODO: or create one
        """
        if f"profile {default_profile}" in content.sections():
            return default_profile

        raise ValueError(f"Cannot find specified default profile {default_profile}")
