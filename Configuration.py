import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Define variables from config.ini
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

CHANNEL_ID = config.get('DISCORD-INFO', 'CHANNEL_ID')
