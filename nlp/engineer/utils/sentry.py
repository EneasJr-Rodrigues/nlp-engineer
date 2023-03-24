from datetime import datetime
import sentry_sdk
from pytz import timezone

# FIXME: Sentry Apache Pyspark Integration is currently unmaintained https://github.com/getsentry/sentry-python/issues/1102
# from sentry_sdk.integrations.spark import SparkIntegration, SparkWorkerIntegration
# import pyspark.daemon as original_daemon


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Sentry(metaclass=Singleton):
    def __init__(self):
        self.sdk_connected = False
        self.daemon_connected = False
        self.default_tags = {}

    @staticmethod
    def _log(msg):
        sao_paulo_timezone = timezone('America/Sao_Paulo')
        print(f'[{datetime.now().astimezone(sao_paulo_timezone).strftime("%m/%d %H:%M:%S")}] - {msg}')

    def set_dns(self, dns: str):
        self.dns = dns

    def connect(self):
        if not self.sdk_connected and self.dns:
            self._log('[INFO] Setting up Sentry')
            sentry_sdk.init(self.dns, traces_sample_rate=1.0)  # , integrations=[SparkIntegration()])

            self.sdk_connected = True

    def initialize_daemon(self):
        if not self.daemon_connected and self.dns:
            self._log(f'[INFO] Setting up sentry daemon {self.dns}')
            sentry_sdk.init(self.dns, traces_sample_rate=1.0)  # , integrations=[SparkWorkerIntegration()])
            # original_daemon.manager()
            self._log('[INFO] Finished setting up sentry daemon')

            self.daemon_connected = True

    def add_breadcrumb(self, message, level, data: dict = None, category: str = 'logger', type: str = 'info'):
        if self.sdk_connected or self.daemon_connected:
            sentry_sdk.add_breadcrumb(type=type, category=category, message=message, level=level, data=data)

    def capture_message(self, message: str, level: str = 'info'):
        if self.sdk_connected or self.daemon_connected:
            sentry_sdk.capture_message(message=message, level=level)

    def set_default_tags(self, tags):
        self.default_tags = tags
        if self.sdk_connected or self.daemon_connected:
            for key, value in tags.items():
                self.set_tag(key, value)

    def set_tag(self, key: str, value: str):
        if self.sdk_connected or self.daemon_connected:
            sentry_sdk.set_tag(key, value)

    def set_transaction_tags(self, transaction_instance=None):
        if self.sdk_connected or self.daemon_connected:
            transaction = transaction_instance or sentry_sdk.Hub.current.scope.transaction
            # self._log(f'[DEBUG] [Sentry] Setting Tag {transaction}')
            if transaction:
                # self._log('[DEBUG] [Sentry] Setting Tag to transaction')
                for key, value in self.default_tags.items():
                    transaction.set_tag(key, value)

    def capture_exception(self, error, extra={}):
        if self.sdk_connected or self.daemon_connected:
            with sentry_sdk.push_scope() as scope:
                for key, value in self.default_tags.items():
                    scope.set_tag(key, value)
                for key, value in extra.items():
                    scope.set_extra(key, value)

                sentry_sdk.capture_exception(error, scope=scope)


sentry = Sentry()
