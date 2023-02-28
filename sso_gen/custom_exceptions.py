# coding=utf-8
"""
App specific exceptions
"""


class NeedNewToken(Exception):
    """If there is no cached token"""


class CommandError(Exception):
    """If there was a problem running a shell command"""


class CantAccessAccount(Exception):
    """Problem accessing the account"""
