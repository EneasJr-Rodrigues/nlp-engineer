from pyspark.sql import DataFrame
from pyspark import StorageLevel
from .remove_names import remove_names
from .remove_personal_data import (
    remove_telephone_number,
    remove_personal_document,
    remove_address_info,
    remove_car_info,
    hash_columns,
)
from utils import logger, decorators


@decorators.recipe_step
@decorators.record_performance
def anonymizer(df: DataFrame, recipe: dict) -> DataFrame:
    """
    Anonymizes dataframe based on recipe.

    Depending on the steps specified in the recipe, this function will remove names, personal documents, phone numbers, postal codes and car plates

    :param df: The DataFrame that will be anonymized
    :type df: DataFrame

    :param recipe: Recipe that describes how the anonymization will happen
    Ex:
    {
        'anonymizer':
        {
            'steps':
            {
                'hash_columns':
                {
                    'columns': ['']
                }
                'remove_names':
                {
                    'columns': ['']
                },
                'remove_personal_document':
                {
                    'columns': ['']
                },
                'remove_telephone_number':
                {
                    'columns': ['']
                }
            }
        }
    }
    :type recipe: dict

    :return: anonymized dataframe
    :rtype: DataFrame
    """

    steps = recipe['steps']
    rm_names_params = steps['remove_names']

    logger.info('[anonymizer] Convert personal identity in a hash code')
    df = hash_columns(df, recipe=steps)

    logger.info('[anonymizer] Removing Personal Document')
    df = remove_personal_document(df, steps['remove_personal_document']['columns'])

    logger.info('[anonymizer] Removing Telephones')
    df = remove_telephone_number(df, steps['remove_telephone_number']['columns'])

    logger.info('[anonymizer] Removing Address')
    df = remove_address_info(df, steps['remove_address_info']['columns'])

    logger.info('[anonymizer] Removing Car Info')
    df = remove_car_info(df, steps['remove_car_info']['columns'])

    df = df.checkpoint()
    logger.info('[anonymizer] Removing Names')
    df = remove_names(
        df,
        rm_names_params['columns'],
        rm_names_params['most_frequent'],
        rm_names_params['extra_names'],
        rm_names_params['client_name_column'],
    )

    return df
