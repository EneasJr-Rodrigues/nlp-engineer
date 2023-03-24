from pyspark.sql import DataFrame, functions as F

from .colorize import Colorize
from .logger import logger

from .custom_requests import RequestObjects

from .validate_key import validate_key
from .remove_words_from_df import remove_words_from_df
from .contains import contains_udf



def filter_empty(column):
    return (F.col(column).isNotNull()) & (F.col(column) != '') & (F.col(column) != ' ')


def debugger(
    df, message='>>>>Debugger<<<<', show=True, save_df=True, save_name='debugger.parquet', limit=20, is_truncated=True
):
    """
    Display and save a parquet from a running processor

    :param df: {DataFrame} Input Data Frame.
    :message: (opt) Message to display in console
    :show: (opt) Control console message
    :is_truncated: (opt) Show full log
    :limit: (opt) Limit rows on display message
    :save_df: (opt) Control save a parquet file
    :save_name: (opt) Customize name of output file
    """
    if message:
        print(f'\x1b[1;32m ------------------- {message} --------------------\x1b[0m')
    if show:
        df.limit(limit).show(truncate=(not is_truncated))
    if save_df:
        df.write.mode('overwrite').save(f'../datalake/tmp/{save_name}')
