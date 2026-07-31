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

def print_2D_shape_from_dataframe(df_shape: tuple, msg: str="DataFrame Shape") -> None:
    """
    Print the shape of a 2D DataFrame in a formatted way.
    Args:
        df_shape (tuple): The shape of the DataFrame (rows, columns).
        msg (str): A message to display before the shape information.
    """
    rows, columns = df_shape
    print(f"{msg} > rows: '{rows}', columns: '{columns}'", sep='')