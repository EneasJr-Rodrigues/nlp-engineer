from .logger import logger
from .colorize import Colorize

from pyspark.sql import DataFrame, functions as F, types as T


def remove_words_from_df(df: DataFrame, content_columns: list, words: list) -> DataFrame:
    """
    > The array `words_to_filter` can accept regexes.

    :param df: {DataFrame} Data Frame.
    :return: Data Frame with `content_column` column without unwanted words.
    """

    words = [fr'(?i)\b{word}\b' for word in words]
    extra_words = ['confidential', r'cpf|cnpj', 'telefone', r'(https|http|www)\w+', 'endereco']
    words = words + extra_words

    logger.info(content_columns)
    for content_column in content_columns:
        for pattern in words:
            logger.debug(
                f'{Colorize.get_color("remove_words_from_df", color="magenta", style="bold")} -> Applying REGEX "{pattern}"'
            )
            df = df.withColumn(content_column, F.regexp_replace(F.col(content_column), pattern, ''))

    return df


__all__ = ['remove_words_from_df']
