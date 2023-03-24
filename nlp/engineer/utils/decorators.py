import functools
from .logger import logger
from .colorize import Colorize
from datetime import datetime
from sentry_sdk import start_transaction, start_span
from .sentry import sentry
from os import getenv
import traceback
from pyspark.sql import DataFrame


ENV = getenv('ENV', 'local')


def debug(func):
    """Prints the function signature and return value
    Ex.:
    >>> make_greeting("Richard", age=112)
    Calling make_greeting('Richard', age=112)
    'make_greeting' returned 'Whoa Richard! 112 already, you are growing up!'
    'Whoa Richard! 112 already, you are growing up!'
    """

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]
        signature = ', '.join(args_repr + kwargs_repr)
        logger.debug(
            f'{Colorize.get_color("[decorator.debug]", color="yellow", style="bold")} Calling {func.__name__}({signature})'
        )
        start_time = datetime.now()
        value = func(*args, **kwargs)
        end_time = datetime.now()
        time_diff = end_time - start_time
        logger.debug(
            f'{Colorize.get_color("[decorator.debug]", color="yellow", style="bold")} [{time_diff.total_seconds()}] {func.__name__!r} returned {value!r}'
        )
        return value

    return wrapper_debug


def recipe_step(_func=None, *, step_name='', verify_only=False):
    """ Verifies if step is mentioned on recipe before calling it """

    def decorator_recipe_step(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            recipe = kwargs['recipe']
            step = step_name or func.__name__
            logger.debug(
                f'{Colorize.get_color("[decorator.recipe_step]", color="yellow", style="bold")} Checking if "{Colorize.get_color(step, color="magenta")}" is on recipe {recipe.keys()} = {step in recipe.keys()}'
            )
            if step in recipe.keys() and recipe[step]:
                logger.debug(
                    f'{Colorize.get_color("[decorator.recipe_step]", color="yellow", style="bold")} "{step}" is fullfilled {recipe[step]}'
                )
                kwargs['recipe'] = recipe[step]
                logger.debug(
                    f'{Colorize.get_color("[decorator.recipe_step]", color="yellow", style="bold")} Calling "{step}" args: {args} kwargs: {kwargs.items()}'
                )
                if verify_only:
                    return func(*args)
                return func(*args, **kwargs)
            df = kwargs['df'] if 'df' in kwargs else args[0]
            logger.debug(
                f'{Colorize.get_color(f"[Counting rows after executing method {step}]", color="yellow", style="bold")} {df.count()}'
            )
            return df

        return wrapper

    if _func is None:
        return decorator_recipe_step
    else:
        return decorator_recipe_step(_func)


def record_performance(_func=None, *, step_name='', macro_step=False, eager=True):
    """Record step performance and send to Sentry Platform"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            step = step_name or func.__name__
            logger.debug(
                f'{Colorize.get_color("[decorator.record_performance]", color="yellow", style="bold")} Recording {"Transaction" if macro_step else "Transaction.Span"} "{Colorize.get_color(step, color="magenta")}"'
            )

            if macro_step:
                with start_transaction(name=step) as transaction:
                    sentry.set_transaction_tags(transaction)
                    return func(*args, **kwargs)

            with start_span(op=step) as span:
                try:
                    span.set_tag('transaction.task', step)
                    sentry.set_transaction_tags(span)

                    if not eager:
                        return func(*args, **kwargs)

                    df = func(*args, **kwargs)

                    logger.debug(
                        f'{Colorize.get_color("[decorator.record_performance]", color="yellow", style="bold")} Running DataFrame checkpoint for {step}'
                    )

                    # try:
                    #     if ENV not in ['local', 'test']:
                    #         df = df.checkpoint()
                    # except Exception as error:
                    #     if 'Py4JJavaError' in type(error).__name__:
                    #         logger.error('Checkpoint directory not defined')
                    #     else:
                    #         raise error

                    return df
                except Exception as error:
                    logger.error(f'[{step}] failed! {error.args}')
                    df_info = {'df_count': None, 'df_columns': None}
                    df = None

                    if 'df' in kwargs:
                        df = kwargs['df']
                    elif args:
                        df = args[0]
                    logger.info(f'[Sentry Decorator] df type {type(df)}')
                    if df and isinstance(df, DataFrame):
                        df_info['df_count'] = df.count()
                        df_info['df_columns'] = df.columns

                    sentry.capture_exception(error, extra=df_info)
                    raise error

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)
