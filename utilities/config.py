import pickle
import os
from configparser import ConfigParser 


parser = ConfigParser()
parser.read('utilities/config.ini')

credential_file = parser['credentials']['credential_file']
# filepath = os.path.abspath('utilities/config.pkl')
with open(credential_file, 'rb') as f:
    credentials = pickle.load(f)

db_config = {
    'host': parser['dbconfig']['host'],
    'port': parser['dbconfig']['port'],
    'dbname': parser['dbconfig']['dbname'],
    'user': credentials['db']['user'],
    'password': credentials['db']['password'],
}

finnhub_config = credentials['finnhub']
MAX_TRY = int(parser['setting']['max_try'])
# db_config = config['db']