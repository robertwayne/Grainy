import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scope)
gc = gspread.authorize(credentials)
sheet = gc.open("SafehouseStash").sheet1