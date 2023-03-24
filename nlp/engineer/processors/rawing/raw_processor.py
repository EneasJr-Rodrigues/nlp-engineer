from pyspark.sql import DataFrame, functions as F, types as T
from .anonymizer import anonymizer
from utils import logger, decorators
from pyspark import StorageLevel
from nlp.engineer.processors.rawing.recipe import convert_json
from nlp.engineer.processors.rawing.anonymizer import adjust_columns
import pandas as pd


class Rawing(RawingProcessor):
    @decorators.record_performance(step_name='Rawing.call_process', macro_step=True)
    def __init__(self, 
                recipe: dict,
                df: DataFrame
                ):
            
        self.recipe = recipe
        self.df = df

        super().__init__()
    
    @classmethod
    def call_process(self, recipe, df):
        recipe_formated = convert_json(recipe)
        df = adjust_columns(df)
        df = RawingProcessor.call(self, recipe=recipe_formated, df=df)
        return df


class RawingProcessor(Rawing):
    def call(self, recipe: dict, df: DataFrame) -> DataFrame:
        if not df:
            print('No data to process!')
            return None
        
        recipe, df = Rawing.call_process(df=df, recipe=recipe)
        logger.info(f'[Rawing Processor] DF lines x columns: {df.count()} x {len(df.columns)}')

        logger.info('Starting Rawing Processor')
        df = anonymizer(df, recipe=recipe)

        recipe_columns = recipe['export']['columns'] + ['P_YEAR', 'P_MONTH', 'P_DAY']

        columns_to_export = [column for column in recipe_columns if column in df.columns]

        df = df.select(columns_to_export)
        df.explain(True)
        logger.info('[Rawing Processor] Checkpoint Done')

        df = RawingProcessor.save(self, df, recipe=recipe)
        logger.info('[Rawing Processor] Finishing Done')

        return df

    @decorators.record_performance(step_name='RawingProcessor.save', macro_step=True)
    def save(self, df, recipe):
        """
        Write data with Csv
        """
        path_save = recipe['path_file']

        logger.info('Saving Raw Dataframe')
        logger.info(f'Columns processed: {self.processed.columns}')

        filename_renomead = 'rawing_tratado'
        file_save = f'{filename_renomead}.csv'
        df = df.toPandas()
        df.to_csv(f'{path_save}/{file_save}', sep=';',encoding='utf-8',index=False)
        logger.info('Finishing Process') 

        logger.info(f'dataframe schema: \n {df.printSchema()}')
        return df

__all__ = ['call_process']