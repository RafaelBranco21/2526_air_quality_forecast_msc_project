"""General-purpose utility functions for the generic_code package."""


def print_sep(length: int = 80, char_to_use: str = "=", end_newline: bool = False) -> None:
    """Print a separator line of a specified length.

    Args:
        length (int): The length of the separator line. Default is 80.
        char_to_use (str): The character to use for the separator. Default is '='.
        end_newline (bool): If True, prints an extra newline after the separator. Default is False.

    Returns:
        None
    """
    print(char_to_use * length)
    if end_newline:
        print()
