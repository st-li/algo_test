from stock_reader import load_splits, load_daily_data
from datetime import datetime, timedelta


if __name__ == '__main__':
    with open('data_input/symbol_list.txt') as f:
        symbols = [line.strip() for line in f]

    # load_splits(datetime.now()-timedelta(5), datetime.now())
    # load_splits(datetime(2000, 1, 1), datetime.now())
    load_daily_data(datetime.now()-timedelta(1), datetime.now(), symbols)
    # load_daily_bulk(datetime(2000, 1, 1), datetime.now(), symbols)