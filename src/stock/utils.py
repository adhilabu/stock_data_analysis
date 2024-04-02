import pandas as pd

def get_rounded_value(
        value: float,
        decimal_place: int = 2
    ) -> float:
    """
    method to fetch rounded value with default decimal place as two.
    """
    return round(value, decimal_place)

def get_start_and_step_from_df(
        df: pd.DataFrame,
        divisor: int = 10,
    ) -> tuple[int, int]:
    """
    method to fetch start and step for the pandas dataframe.
    """
    # get the count of total rows which is divisible by divisor ^ 2
    divisor_val = divisor * divisor
    total_count = df.shape[0] // divisor_val * divisor_val

    # calculate both start and step based on the total count and divisor
    start = int(total_count / divisor)
    step = int(start / divisor)

    return start, step

