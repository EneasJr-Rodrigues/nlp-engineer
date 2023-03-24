from pyspark.sql import DataFrame, functions as F, types as T
import re


def contains(pattern, text):
    if text is None:
        return None
    else:
        return int(re.search(pattern, text) is not None)


contains_udf = F.udf(lambda pattern, text: contains(pattern, text), T.LongType())

__all__ = ['contains_udf']
