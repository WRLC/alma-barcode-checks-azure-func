"""
Shared utilities for the project.
"""
import logging
import os


def check_envs(envs: dict[str, str]) -> None:
    """
    Check if the environment variables are set.

    :param envs: List of environment variables to check
    :return: None
    """
    for env in envs.values():
        if not os.getenv(env):
            logging.error("%s not set", env)
            raise ValueError(f"{env} not set")
