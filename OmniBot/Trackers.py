import grequests
import asyncio
import discord
from robobrowser import RoboBrowser
from OmniBot import Configuration as ini
import datetime
import re
import sys
from OmniBot.Client import client


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
        # global_tonnage = br.find()

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


class Item:
    name = ""
    item_type = ""
    value = 0
    in_circulation = 0

    def toS(self):
        return "{} {} {}".format(self.name, self.item_type, self.value, self.in_circulation)


class Weapon(Item):
    damage = 0
    accuracy = 0
    stealth = 0

    def toS(self):
        return "{} {} {} {}".format(self.super.toS(), self.damage, self.accuracy, self.stealth)


def get_item_stats(item_number):
    br.open('https://www.zapoco.com/item/{}'.format(item_number))

    # regexes for different types of data
    type_re = re.compile(r'<h4 class="text-bold text-light">(\w+)</h4>')
    value_re = re.compile(r'<h4 class="text-bold text-light">(<i class="fa fa-medkit"></i> )??(\d+(,\d{3})*)</h4>')
    progress_re = re.compile(r'<div class="progress" style="width:(\d+)%"></div>')

    # grab the correct html snippets, as strings
    type_div = "{}".format(br.select('h4.text-light.text-bold')[0])  # Type
    value_div = "{}".format(br.select('h4.text-light.text-bold')[1])  # Value
    circulation_div = "{}".format(br.select('h4.text-light.text-bold')[3])  # In Circulation

    # use regex to get the interesting data
    i = Item()
    i.item_type = type_re.match(type_div)[1]
    i.value = value_re.match(value_div)[2]
    i.in_circulation = value_re.match(circulation_div)[2]

    if i.item_type == 'Weapon':
        w = Weapon()
        w.super = i

        damage_div = "{}".format(br.select('div.progress')[3]) # Damage
        accuracy_div = "{}".format(br.select('div.progress')[4]) # Accuracy
        stealth_div = "{}".format(br.select('div.progress')[5]) # Stealth

        w.damage = progress_re.match(damage_div)[1]
        w.accuracy = progress_re.match(accuracy_div)[1]
        w.stealth = progress_re.match(stealth_div)[1]

        return w

    return i

# Usage: i = get_item_stats(br, item_number)


# inventory parser: returns a dict with all items in inventory of the currently logged in player
async def parse_inventory():
    br.open('https://www.zapoco.com/inventory')
    item_re = re.compile(r'<div class="pull-left pd-h-sm">\s*<a class="text-light text-strong" '
                         r'href="https://www.zapoco.com/item/(\d+)">(.*)</a> x(\d+)\s*</div>')

    selection = br.select('div.pull-left.pd-h-sm')

    inventory = {}

    for div in selection:
        # match item name, amount
        # no match -> no item
        match = item_re.match('{}'.format(div))
        if match is not None:
            item_number = match[1]
            item = match[2]
            count = match[3]
            inventory[item] = count  # item's can't be listed twice so we don't have to check for duplicates

    print(inventory)
    return inventory


# land scraping code
async def get_land_stats(browser, acre_number):
    browser.open('https://www.zapoco.com/land/acre/{}'.format(acre_number))
    user_re = re.compile(r'<span class="text-light">Owned by '
                         r'<a href="https://www.zapoco.com/user/\d+">'
                         r'<span[^>]*>(\w+).*</span></a> \(owns (\d+) acres\)</span>')
    selection = browser.select('span.text-light')

    if selection is None or selection == []:
        # print('acre not owned')
        return None, 0

    if acre_number in []:  # list should contain all the lands that the bot owns (land numbers)
        # print('Self owned')
        return None, 0  # hard coded stats: the bot's name and the number of land it owns

    match = None

    for div in browser.select('span.text-light'):
        match = user_re.match('{}'.format(div))
        if match is not None:
            return '{}'.format(match[1]), '{}'.format(match[2])

    print('Something went wrong parsing acre {}'.format(acre_number))
    return None, 0


def map_land_owners(browser, file=None):
    users = {}
    first = 1
    last = 7882

    for acre in range(first, last+1):
        user, acres = get_land_stats(browser, acre)
        if user is not None and user not in users:
            users[user] = acres
            if file is None:
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
    # I don't think we get to this, so it never runs
    await get_npc_health()
    print('debug: we made it to get_npc_health!')
