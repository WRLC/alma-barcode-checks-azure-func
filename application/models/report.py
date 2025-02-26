"""
Report model
"""
from typing import Any


class Report:  # pylint: disable=too-few-public-methods
    """
    Report object
    """
    def __init__(self, data: dict[str, Any]) -> None:
        """
        Report object

        :param data: json
        :return: None
        """
        self.data = data

    def __str__(self) -> str:
        """
        Return the report as a string

        :return: str
        """
        return f"{self.data}"
