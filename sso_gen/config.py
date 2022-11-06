# coding=utf-8
"""Configuration settings for the app"""

# Standard Library
import os

# Third Party Libraries
from decouple import config

BASE_DIR = os.path.join(os.path.expanduser("~"), ".aws")

# Get env vars
DEFAULT_PROFILE = config("DEFAULT_PROFILE", default="login")
DEBUG = config("DEBUG", default=False, cast=bool)
MAX_SSO_RETRIES = config("MAX_SSO_RETRIES", default=1, cast=int)
COMPANY = config("COMPANY", default="myorg")
SSO_START_URL = config("SSO_START_URL", default="")

if not SSO_START_URL:
    raise ValueError("SSO_START_URL required")

files = {
    "cache_dir": os.path.join(BASE_DIR, "sso", "cache"),
    "config_file": os.path.join(BASE_DIR, "config"),
    "credentials_file": os.path.join(BASE_DIR, "credentials"),
}

aws = {
    "sso_start_url": SSO_START_URL,
    "org_prefix": f"{COMPANY}-",
    "base_profile": "profile " + config("BASE_PROFILE", default="login"),
    "account_map": {
        "123456789012": "org",
        "999999999999": "dev",
        "888888888888": "prd",
    },
}
