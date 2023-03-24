from pyspark.sql import DataFrame, functions as F, types as T
from utils import logger, decorators


@decorators.record_performance
def remove_telephone_number(df: DataFrame, columns: list) -> DataFrame:
    """
    Removes telephone number from the DataFrame.

    Uses regex expressions to replace all phone and telephone numbers with "_confidential_" in the specified columns

    :param df: DataFrame that will be altered
    :type df: DataFrame
    :param columns: DataFrame columns that will be altered
    :type columns: list
    :return: Altered DataFrame
    :rtype: DataFrame
    """

    celphone_pattern = r'(\d{2}|\(\d{2}\))[ .-]?\d{1}\s?\d{4}([ .-]?)\d{4}|(\d{2}|\(\d{2}\))[ .-]?\d{4}([ .-]?)\d{4}|(\d{1}\s?\d{4}|\d{4,})[ .-]?\d{4}'
    phone_pattern = r'\(\d{2}\)\d{4}-?\d{4}\b|\b\d{4}-?\d{4}\b'

    for column in columns:
        logger.info(f'[Remove Telephone Number] Cleaning column {column}')
        df = df.withColumn(column, F.regexp_replace(F.col(column), celphone_pattern, '_confidential_'))
        df = df.withColumn(column, F.regexp_replace(F.col(column), phone_pattern, '_confidential_'))
    return df


@decorators.record_performance
def remove_personal_document(df: DataFrame, columns: list) -> DataFrame:
    """
    Removes personal documents from the DataFrame.

    Uses regex expressions to replace all CPFs, CNPJs and RGs with "_confidential_" in the specified columns

    :param df: DataFrame that will be altered
    :type df: DataFrame
    :param columns: DataFrame columns that will be altered
    :type columns: list
    :return: Altered DataFrame
    :rtype: DataFrame
    """

    cpf_pattern = r'\b\d{3}.?\d{3}.?\d{3}-?\d{2}\b|\b\d{11}\b'
    cnpj_pattern = r'\b\d{2}.?\d{3}.?\d{3}\/\d{4}-?\d{2}\b|\b\d{14}\b'
    rg_pattern = r'\b\d{2}\.?\d{3}\.?\d{3}-?\d\b'

    for column in columns:
        logger.info(f'[Remove Personal Document] Cleaning column {column}')
        df = df.withColumn(column, F.regexp_replace(F.col(column), cpf_pattern, '_confidential_'))
        df = df.withColumn(column, F.regexp_replace(F.col(column), cnpj_pattern, '_confidential_'))
        df = df.withColumn(column, F.regexp_replace(F.col(column), rg_pattern, '_confidential_'))
    return df


@decorators.record_performance
def remove_address_info(df: DataFrame, columns: list) -> DataFrame:
    """
    Removes postal codes from the DataFrame.

    Uses regex expressions to replace all postal codes (CEP) with "_confidential_" in the specified columns

    :param df: DataFrame that will be altered
    :type df: DataFrame
    :param columns: DataFrame columns that will be altered
    :type columns: list
    :return: Altered DataFrame
    :rtype: DataFrame
    """

    postal_code_pattern = r'\b\d{2,}[ .-]?\d{3,}[ .-]?\d{3}\b'

    for column in columns:
        logger.info(f'[Remove Address Info] Cleaning column {column}')
        df = df.withColumn(column, F.regexp_replace(F.col(column), postal_code_pattern, '_confidential_'))
    return df


@decorators.record_performance
def remove_car_info(df: DataFrame, columns: list) -> DataFrame:
    """
    Removes car plates from the DataFrame.

    Uses regex expressions to replace all car plates with "_confidential_" in the specified columns

    :param df: DataFrame that will be altered
    :type df: DataFrame
    :param columns: DataFrame columns that will be altered
    :type columns: list
    :return: Altered DataFrame
    :rtype: DataFrame
    """

    car_pattern = r'\b\w{3}[ .-]?\d{4}\b|\b\w{3}[ .-]?\d{1}[ .-]?\w{1}[ .-]?\d{2}\b'

    for column in columns:
        logger.info(f'[Remove Car Info] Cleaning column {column}')
        df = df.withColumn(column, F.regexp_replace(F.col(column), car_pattern, '_confidential_'))
    return df


@decorators.recipe_step
@decorators.record_performance
def hash_columns(df: DataFrame, recipe: dict) -> DataFrame:
    """
    Removes personal identity and converty to hash code.

    Uses functions of sha2 to convert a hash code

    :param df: DataFrame that will be altered
    :type df: DataFrame
    :param columns: DataFrame columns that will be altered
    :type columns: list
    :return: Altered DataFrame
    :rtype: DataFrame

    """

    for column in recipe['columns']:
        logger.info(f'Convert to hash code column: {column}')
        df = df.withColumn(column, F.sha2(F.col(column).cast('string'), 256))

    return df
