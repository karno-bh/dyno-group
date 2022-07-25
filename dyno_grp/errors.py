"""
This module is the aggregation of all custom exception used in the Grouper
"""


class ClauseException(Exception):
    """
    ClauseException may be raised when there is incorrect definition of a clause
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProcessException(Exception):
    """
    ClauseException may be raised when there is a problem of processing data from the stream
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
