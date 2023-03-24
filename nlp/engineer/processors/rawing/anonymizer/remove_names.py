from pyspark.sql import DataFrame, functions as F, types as T
from urllib.request import urlretrieve
from utils import logger, decorators
import pandas as pd
import unicodedata
import re
from flashtext import KeywordProcessor


def anonymizer_dataset(most_frequent=None):
    database_ibge = {
        'url': 'https://drive.google.com/file/d/1cuSO5YtJY1FWdMydB3XDjA6F3q-kg-2m/view?usp=share_link',
        'file_path': './nomes.csv'
    }
    urlretrieve(database_ibge['url'], database_ibge['file_path'])
    df = pd.read_csv(database_ibge['file_path'], usecols=['first_name', 'frequency_total'])
    names = list(df.sort_values(by=['frequency_total'], ascending=False)['first_name'])[:most_frequent]
    logger.info(f'[Remove Names] Using {most_frequent} names from IBGE dataset. First 3: {names[:3]}')
    return names


@F.udf(T.StringType())
def remove_accented_characters(text: str) -> str:
    if text:
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([char for char in nfkd_form if not unicodedata.combining(char)])
    return ''


def extract_names_from_column(df: DataFrame, client_name_column: str) -> list:
    """If a column with the client name (or any specific name) is provided, the column 'regex' is incremented with the content of this column"""
    if not client_name_column:
        return []

    logger.info(f'[Remove Names] Using names in {client_name_column} column')
    return [
        row[client_name_column]
        for row in df.select(F.lower(F.col(client_name_column)).alias(client_name_column)).distinct().collect()
    ]


@decorators.record_performance
def remove_names(
    df: DataFrame, columns: list, most_frequent: int = None, extra_names: list = [], client_name_column: str = None
) -> DataFrame:
    """TODO: doc"""
    processor = KeywordProcessor()

    names = anonymizer_dataset(most_frequent) + extract_names_from_column(df, client_name_column) + extra_names
    logger.info(f'[Remove Names] Using total of {len(names)} names')

    for name in names:
        processor.add_keyword(name, '_name_')

    # remove_accented_characters_udf = F.udf(lambda text: remove_accented_characters(text), T.StringType())
    remove_names_udf = F.udf(lambda text: processor.replace_keywords(text), T.StringType())
    for column in columns:
        logger.info(f'[Remove Names] Removing accented characters from {column} column')
        df = df.withColumn(column, remove_accented_characters(F.col(column)))
    # df = df.checkpoint()

    for column in columns:
        logger.info(f'[Remove Names] Removing names from {column} column with flashtext')
        df = df.withColumn(column, remove_names_udf(F.col(column)))

    logger.info('Names removed')
    return df
