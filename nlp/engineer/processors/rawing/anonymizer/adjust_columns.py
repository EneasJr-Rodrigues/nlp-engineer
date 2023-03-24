from pyspark.sql import DataFrame, functions as F, types as T


def lower_all_col(df):
    for c in df.columns:
        df = df.withColumnRenamed(c, c.lower())
    return df
