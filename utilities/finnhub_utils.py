import finnhub
from contextlib import contextmanager
from logging_conf import MyLogger


logger = MyLogger.logger

@contextmanager
def finnhub_connection(api_key):
    try:
        finnhub_client = finnhub.Client(api_key=api_key)
        yield finnhub_client
    except Exception as e:
        logger.error(e)
        raise
    finally:
        finnhub_client.close()