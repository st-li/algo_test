from utilities.config import db_config, finnhub_config, MAX_TRY
from utilities.postgres_utils import cursor, connection
from utilities.finnhub_utils import finnhub_connection
from utilities.stringio_utils import buildStringIO
from logging_conf import MyLogger
from datetime import timezone, date, timedelta, datetime
from typing import List
import pandas as pd


logger = MyLogger.logger

def gen_splits(date_from: str, date_to: str):
    import time
    with open('data_input/symbol_list.txt') as f:
        symbols = [line.strip() for line in f]
    with finnhub_connection(finnhub_config['api']) as finnhub_client:
        for symbol in symbols:
            res = {}
            stock_data = None
            trials = MAX_TRY
            t1 = time.perf_counter()
            while trials:
                try:
                    stock_data = finnhub_client.stock_splits(
                        symbol, 
                        _from=date_from.strftime('%Y-%m-%d'),
                        to=date_to.strftime('%Y-%m-%d')
                    )
                    break
                except Exception:
                    trials -= 1
                    logger.info(f'Fail to read split data for {symbol}')
            if not trials:
                logger.error(f'Cannot get valid data of {symbol} after {MAX_TRY} tries.')
            if stock_data:
                res['symbol'] = symbol
                res['data'] = stock_data
                res['t'] = t1
            else:
                res['symbol'] = symbol
                res['data'] = None
                res['t'] = t1
            yield res


def gen_daily(date_from: datetime, date_to: datetime, symbols: List[str]):
    import time
    with finnhub_connection(finnhub_config['api']) as finnhub_client:
        for symbol in symbols:
            # t1 = time.perf_counter()
            res = {}
            stock_data = None
            trials = MAX_TRY
            t1 = time.perf_counter()
            while trials:
                try:
                    stock_data = finnhub_client.stock_candles(
                        symbol, 'D', 
                        int(date_from.timestamp()), 
                        int(date_to.timestamp()))
                    break
                except Exception:
                    trials -= 1
                    logger.info(f'{symbol} fail to get data this time')
            if not trials:
                logger.error(f'Cannot get valid data of {symbol} after {MAX_TRY} tries.')
            if stock_data and stock_data['s'] == 'ok':
                df = pd.DataFrame(stock_data)
                df['t'] = pd.to_datetime(df['t'], unit='s')
                df['v'] = df['v'].astype('int64')
                df.drop(columns='s', inplace=True)
                df.columns = ['close', 'high', 'low', 'open', 'time', 'volume']
                df['symbol'] = symbol
                res['symbol'] = symbol
                res['data'] = df
                res['t'] = t1
            else:
                res['symbol'] = symbol
                res['data'] = None
                res['t'] = t1
            yield res

def load_daily_data(date_from: datetime, date_to: datetime, symbols: List[str]):
    import time
    count = 0
    seconds = 0
    with cursor(
        db_config['host'], 
        db_config['port'], 
        db_config['user'], 
        db_config['password'], 
        db_config['dbname']) as cur:
        conn = cur.connection
        for stock_data in gen_daily(date_from, date_to, symbols):
            t1 = stock_data['t']
            symbol = stock_data['symbol']
            length = len(stock_data['data']) if stock_data['data'] is not None else 0
            if stock_data['data'] is not None:
                with buildStringIO() as temp_file:
                    stock_data['data'].to_csv(temp_file, header=False, index=False, line_terminator='\n')
                    temp_file.seek(0)
                    cur.copy_from(temp_file, 'daily', sep=',', columns=['close', 'high', 'low', 'open', 'time', 'volume', 'symbol'])
                    conn.commit()
                t2 = time.perf_counter()
                count += 1
            else:
                t2 = time.perf_counter()
                count += 1
                logger.error(f'{symbol} has no data')
            seconds += t2-t1
            if count == 59:
                if seconds < 60:
                    logger.info(f'sleep {62-seconds} seconds')
                    time.sleep(62 - seconds)
                count = 0
                seconds = 0
            logger.info(f'It takes {t2 - t1} seconds to handle {symbol}, total records count is {length}, {count} stocks in 1 minute')

def load_splits(date_from: datetime, date_to: datetime):
    import time
    count = 0
    seconds = 0

    with cursor(
        db_config['host'], 
        db_config['port'], 
        db_config['user'], 
        db_config['password'], 
        db_config['dbname']) as cur:
        # conn = cur.connection
        for stock_data in gen_splits(date_from, date_to):
            t1 = stock_data['t']
            symbol = stock_data['symbol']
            if stock_data['data'] is not None:
                # logger.info(str(stock_data['data']))
                data = ',\n'.join(
                    ["('{}', '{}', {}, {})".format(stock["symbol"], stock["date"], stock["fromFactor"], stock["toFactor"]) 
                    for stock in stock_data['data']]
                )
                insert_query = f"""
                    INSERT INTO splits
                    (symbol, split_date, fromfactor, tofactor)
                    VALUES
                    {data};
                """
                cur.execute(insert_query)
                t2 = time.perf_counter()
                count += 1
            else:
                t2 = time.perf_counter()
                count += 1
                logger.error(f'{symbol} has no data')
            seconds += t2-t1
            if count == 59:
                if seconds < 60:
                    logger.info(f'sleep {62-seconds} seconds')
                    time.sleep(62 - seconds)
                count = 0
                seconds = 0
            logger.warning(f'It takes {t2 - t1} seconds to handle {symbol}, {count} stocks in 1 minute')