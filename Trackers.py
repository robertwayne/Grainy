import grequests
import asyncio
import discord
from robobrowser import RoboBrowser
import Configuration as ini
import datetime
import re
from Client import client


# Build a session and submit log-in data upon initialization
headers = {
    "Connection": "keep-alive"
}

session = grequests.Session()
session.headers = headers
br = RoboBrowser(session=session, parser='html.parser', history=True)
br.open('{url}'.format(url=ini.LOGIN_URL))

form = br.get_form()
form['username'] = '{usr}'.format(usr=ini.BOT_USERNAME)
form['password'] = '{pwd}'.format(pwd=ini.BOT_PASSWORD)
try:
    br.submit_form(form)
except SyntaxError:
    print("Form submission failed. Invalid log-in data.")


async def get_grain_price():
    previous_price = 0

    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(ini.UPDATE_RATE)
        br.open('{url}'.format(url=ini.LAND_URL))
        result = br.find('h2', {'class': '{pcs}'.format(pcs=ini.PRICE_CSS_SELECTOR)}).get_text()
        #global_tonnage = br.find()

        # replace 'result' commas with whitespace and convert to a float
        r = result.replace(',', '')
        price = (float(r))
        dt = datetime.datetime.utcnow()

        if price > ini.EVERYONE_ALERT_THRESHOLD and previous_price != r:
            print('@everyone Grain Price: ' + r)
            em = discord.Embed(title="Grain Alert",
                               url="https://www.zapoco.com/land/grain",
                               description="**Price: " + r + "**",
                               color=0x783e8e,
                               timestamp=dt)
            await client.send_message(client.get_channel(ini.OMNIBOT_CHANNEL_ID),  '@everyone', embed=em)
            previous_price = r
            await asyncio.sleep(ini.UPDATE_RATE)
        elif price > ini.ALERT_THRESHOLD and previous_price != r:
            print('Grain Price: ' + r)
            em = discord.Embed(title="Grain Alert",
                               url="https://www.zapoco.com/land/grain",
                               description="**Price: " + r + "**",
                               color=0x783e8e,
                               timestamp=dt)
            await client.send_message(client.get_channel(ini.OMNIBOT_CHANNEL_ID), embed=em)
            previous_price = r
            await asyncio.sleep(ini.UPDATE_RATE)


async def get_npc_health():
    channel = client.get_channel(ini.RAID_CHANNEL_ID)
    previous_guard_hp = '670/670'

    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(1)
        br.open('https://www.zapoco.com/user/4')
        guard_hp = br.find(string=re.compile('670'))

        if guard_hp != '670/670' and guard_hp <= previous_guard_hp:
            print('Guard Health: ' + guard_hp)
            await client.send_message(channel, 'The Guard has been attacked! Current health: ' + guard_hp)
            previous_guard_hp = guard_hp
        await asyncio.sleep(60)


# async def get_rare_items():
#     channel = client.get_channel('')
#     cylinder_circulation = 0
#
#     # this shit needs to be iterated through...
#     # tom why the fuck are all your css selectors the exact same name???
#     while not client.is_closed:
#         await asyncio.sleep(60)
#         br.open('https://www.zapoco.com/item/120')
#         result = br.find('h4', {'class': 'text-bold text-light'})





# inventory parser: returns a dict with all items in inventory of the currently logged in player
def parse_inventory(browser):
    browser.open('https://www.zapoco.com/inventory')
    item_re = re.compile(r'<div class="pull-left pd-h-sm">\s*<a class="text-light text-strong" href="https://www.zapoco.com/item/(\d+)">(.*)</a> x(\d+)\s*</div>')

    selection = browser.select('div.pull-left.pd-h-sm')

    inventory = {}

    for div in selection:
        # match item name, amount
        # no match -> no item
        match = item_re.match('{}'.format(div))
        if match != None:
            item_number = match[1]
            item = match[2]
            count = match[3]
            inventory[item] = count # item's can't be listed twice so we don't have to check for duplicates

    return inventory




# land scraping code
def get_land_stats(browser, acre_number):
    browser.open('https://www.zapoco.com/land/acre/{}'.format(acre_number))
    user_re = re.compile(r'<span class="text-light">Owned by <a href="https://www.zapoco.com/user/\d+"><span[^>]*>(\w+).*</span></a> \(owns (\d+) acres\)</span>')
    selection = browser.select('span.text-light')

    if (selection == None or selection == []):
        # print('acre not owned')
        return None, 0

    if acre_number in []: # list should contain all the lands that the bot owns (land numbers)
        # print('Self owned')
        return None, 0 # hard coded stats: the bot's name and the number of land it owns

    match = None

    for div in browser.select('span.text-light'):
        match = user_re.match('{}'.format(div))
        if (match != None):
            return '{}'.format(match[1]), '{}'.format(match[2])

    print('Something went wrong parsing acre {}'.format(acre_number))
    return None, 0

def map_land_owners(browser, file=None):
    users = {}
    first = 1
    last = 7882

    for acre in range(first, last+1):
        user, acres = get_land_stats(browser, acre)
        if user != None and user not in users:
            users[user] = acres
            if (file == None):
                print('{} owns {} acres'.format(user, acres))
            else:
                file.write('{}, {}\n'.format(user, acres))
                sys.stdout.write('\r{}/{} done      '.format(acre, last-first+1))
                sys.stdout.flush()

    print('done')

def scrape_lands(browser):
    try:
        file = open("acres.txt", 'w')
        map_land_owners(browser, file)
    finally:
        file.close()





async def run_trackers():
    await get_grain_price()
    await get_npc_health()
    # await get_rare_items()
