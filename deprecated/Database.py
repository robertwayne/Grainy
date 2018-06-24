import pymysql
from discord import Configuration as ini

conn = pymysql.connect(host='{}'.format(ini.DB_HOST),
                       user='{}'.format(ini.DB_USER),
                       password='{}'.format(ini.DB_PASS),
                       db='{}'.format(ini.DB_DATA))
