import psycopg2
from contextlib import contextmanager
from logging_conf import MyLogger


logger = MyLogger.logger

@contextmanager
def connection(host, port, user, password, dbname):
    connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
    try:
        yield connection
    except Exception as e:
        connection.rollback()
        logger.error(e)
        raise
    else:
        connection.commit()
    finally:
        connection.close()

@contextmanager
def cursor(host, port, user, password, dbname):
    with connection(host, port, user, password, dbname) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()