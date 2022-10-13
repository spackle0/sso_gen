# coding=utf-8
"""Class for manipulating AWS configuration and credentials files"""

# Standard Library
import configparser

# Third Party Libraries
from sso import SsoClient

# Custom Libraries
import sso_gen.config as config

CONFIG_FILE = config.files["config_file"]
CREDENTIALS_FILE = config.files["credentials_file"]
PROFILE_PREFIX = config.aws["profile_prefix"]
DEFAULT_PROFILE = config.DEFAULT_PROFILE


class AwsProfiles:
    """
    Manipulates AWS config and credentials.
    """

    __slots__ = "config_file", "credentials_file", "sso_profile", "sso_client"

    def __init__(
        self,
        config_file=CONFIG_FILE,
        credentials_file=CREDENTIALS_FILE,
        prefix=PROFILE_PREFIX,
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

        self.sso_client = SsoClient(self.sso_profile)

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

        print("Getting credentials for:")
        for account in self.sso_client.account_list:
            account_id = account["accountId"]
            for role_info in self.sso_client.get_role_list(account_id):
                role_name = role_info["roleName"]
                try:
                    creds_profile = f"""{config.aws.org_prefix}-{config.aws["account_map"][account_id]}-{role_name}"""
                except KeyError as e:
                    print(
                        f"Can't get map for account {account_id}. New account? SKIPPING"
                    )
                    continue
                config_profile = f"""profile {creds_profile}"""
                print(f"{creds_profile}")

                creds = self.sso_client.get_role_creds(account_id, role_name)

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

        print(f'Writing "{credentials_file}"')
        with open(self.credentials_file["path"], "w") as credentials_file_fp:
            current_credentials.write(credentials_file_fp)

        print(f'Writing "{config_file}"')
        with open(CONFIG_FILE, "w") as config_file_fp:
            current_config.write(config_file_fp)

    @staticmethod
    def check_default_profile(content, default_profile: str):
        """
        Check for the default profile TODO: or create one
        """
        if f"profile {default_profile}" in content.sections():
            return default_profile

        raise ValueError(f"Cannot find specified default profile {default_profile}")
