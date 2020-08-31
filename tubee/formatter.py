import logging


class TabbedExceptionFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return result.replace("\n", f"\n{'':26}")
