# coding=utf-8
"""Testing for sso_gen and aws_profile"""
# Custom Libraries
from sso_gen import __version__


def test_version():
    assert __version__ == "0.1.0"
