# logger.py
from datetime import datetime
from airflow.utils.log.logging_mixin import LoggingMixin
import pendulum

pt = pendulum.timezone('America/Los_Angeles')

class AirflowLogger(LoggingMixin):
    _instance = None

    def __new__(cls, logger_name='airflow.custom'):
        if cls._instance is None:
            cls._instance = super(AirflowLogger, cls).__new__(cls)
            cls._instance.logger_name = logger_name
        return cls._instance

    def info(self, message):
        self.log.info(f"{datetime.now(pt).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {self.logger_name} - {message}")

    def error(self, message):
        self.log.error(f"{datetime.now(pt).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {self.logger_name} - {message}")

    def warning(self, message):
        self.log.warning(f"{datetime.now(pt).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {self.logger_name} - {message}")

    def debug(self, message):
        self.log.debug(f"{datetime.now(pt).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {self.logger_name} - {message}")