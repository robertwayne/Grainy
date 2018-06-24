import configparser


config = configparser.ConfigParser()
config.read('./config/config.cfg')

# Define variables from configuration.ini
BOT_TOKEN = config.get('BOT-INFO', 'BOT_TOKEN')
BOT_USERNAME = config.get('BOT-INFO', 'BOT_USERNAME')
BOT_PASSWORD = config.get('BOT-INFO', 'BOT_PASSWORD')

LOGIN_URL = config.get('GAME-INFO', 'LOGIN_URL')
LAND_URL = config.get('GAME-INFO', 'LAND_URL')
UPDATE_RATE = config.getint('GAME-INFO', 'UPDATE_RATE')
ALERT_THRESHOLD = config.getfloat('GAME-INFO', 'ALERT_THRESHOLD')
LOCALE_DATA = config.get('GAME-INFO', 'LOCALE_DATA')
EVERYONE_ALERT_THRESHOLD = config.getfloat('GAME-INFO', 'EVERYONE_ALERT_THRESHOLD')
PRICE_CSS_SELECTOR = config.get('GAME-INFO', 'PRICE_CSS_SELECTOR')

OMNIBOT_CHANNEL_ID = config.get('DISCORD-INFO', 'OMNIBOT_CHANNEL_ID')
RAID_CHANNEL_ID = config.get('DISCORD-INFO', 'RAID_CHANNEL_ID')
DEV_CHANNEL_ID = config.get('DISCORD-INFO', 'DEV_CHANNEL_ID')
ELEVATED_ROLE_ID = config.get('DISCORD-INFO', 'ELEVATED_ROLE_ID')

DB_HOST = config.get('DATABASE-INFO', 'DB_HOST')
DB_PORT = config.get('DATABASE-INFO', 'DB_PORT')
DB_USER = config.get('DATABASE-INFO', 'DB_USER')
DB_PASS = config.get('DATABASE-INFO', 'DB_PASS')
DB_DATA = config.get('DATABASE-INFO', 'DB_DATA')
