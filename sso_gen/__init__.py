# coding=utf-8
"""
Prompt the user via browser to log in to sso, then populate config/credentials for any
accounts and roles assigned to that user.

Made with a few snippets from https://github.com/kcerdena/aws_sso.
"""
__version__ = "0.1.0"

# Custom Libraries
from sso_gen.aws_profile import AwsProfiles


def main() -> int:
    """
    Query the account information, download the credentials and write out
    configuration files
    """
    configuation_files = AwsProfiles()
    configuation_files.process_credentials()
    configuation_files.write_files()

    return 0
