import os

from dotenv import load_dotenv

load_dotenv()

INDEX_I = 1
INDEX_NUMDOC = 2
INDEX_CLIENT = 5
INDEX_DATE = 6
INDEX_SUM = 14
DOMAIN = os.getenv('DOMAIN')
LOGIN_URL = os.getenv('LOGIN_URL')
SCRAPE_URL = os.getenv('SCRAPE_URL')
SCRAPE_MANAGER_URL = os.getenv('SCRAPE_MANAGER_URL')
