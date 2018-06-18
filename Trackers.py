import grequests
import asyncio
import discord
from robobrowser import RoboBrowser
import Configuration as ini
import datetime
import re
import sys
from Client import client, timestamp
from Database import conn


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

        if price > ini.EVERYONE_ALERT_THRESHOLD and previous_price != r:
            print(timestamp + ': ' + '@everyone Grain Price: ' + r)
            em = discord.Embed(title="Grain Alert",
                               url="https://www.zapoco.com/land/grain",
                               description="**Price: " + r + "**",
                               color=0x783e8e,
                               timestamp=timestamp)
            await client.send_message(client.get_channel(ini.OMNIBOT_CHANNEL_ID),  '@everyone', embed=em)
            previous_price = r
            await asyncio.sleep(ini.UPDATE_RATE)
        elif price > ini.ALERT_THRESHOLD and previous_price != r:
            print(timestamp + ': ' + 'Grain Price: ' + r)
            em = discord.Embed(title="Grain Alert",
                               url="https://www.zapoco.com/land/grain",
                               description="**Price: " + r + "**",
                               color=0x783e8e,
                               timestamp=timestamp)
            await client.send_message(client.get_channel(ini.OMNIBOT_CHANNEL_ID), embed=em)
            previous_price = r
            await asyncio.sleep(ini.UPDATE_RATE)


async def get_npc_health():
    channel = client.get_channel(ini.RAID_CHANNEL_ID)
    previous_welder_hp = '90/90'

    await client.wait_until_ready()
    while not client.is_closed:
        br.open('https://www.zapoco.com/user/1044')
        welder_hp = br.find(string=re.compile('90'))

        if welder_hp == '45/90' and welder_hp < previous_welder_hp:
            print('Welder Health: ' + welder_hp)
            await client.send_message(channel, 'Welder current health: ' + welder_hp)
            previous_welder_hp = welder_hp
            await asyncio.sleep(300)
        await asyncio.sleep(10)


def get_item_name(item_number):
    br.open('https://www.zapoco.com/item/{}'.format(item_number))
    item_name = ''

    name_re = re.compile(r'<h2><span class="text-light text-strong">(.*)</span></h2>')
    name_div = "{}".format(br.select('h2')[0])  # Name
    item_name = name_re.match(name_div)[1]
    return item_name


def get_item_stats(item_number):
    br.open('https://www.zapoco.com/item/{}'.format(item_number))

    item_data = {}

    # regexes for different types of data
    stat_re = re.compile(r'<div class="col-4 space-2">\s*<p>(\w+)</p>\s*<div class="progress-bar"><div class="progress" style="witimestamph:(.*)%"></div>\s*</div>\s*</div>')
    info_re = re.compile(r'<div class="col-3">\s*<h4 class="text-bold text-light">(.*)</h4>\s*<p>(.*)</p>\s*</div>')
    value_re = re.compile(r'<i class="fa fa-medkit"></i>(.*)')
    check_re = re.compile(r'<i class="fa fa-check"></i>')

    # grab the correct html snippets, as strings
    stat_divs = br.select('div.col-4.space-2')
    info_divs = br.select('div.col-3')

    # print(info_divs)
    for div in info_divs:
        match = info_re.match("{}".format(div))
        if match is not None:
            info = match[2]
            value = match[1]
            if info == "Value":
                value = int(value_re.match(value)[1].replace(',', ''))
            elif info == "Purchasable":
                if check_re.match(value) is None:
                    value = 'Yes'
                else:
                    value = 'No'
            elif info == "In Circulation":
                info = 'Circulation'
                value = int(value.replace(',', ''))

            item_data[info] = value
            # print('{}: {}'.format(info, value))

    # hard coded bot max stats; used for normalization
    bot_eng = 100
    bot_nerve = 10
    bot_hap = 5750
    bot_life = 100

    # print(stat_divs)
    for div in stat_divs:
        # print(div)
        match = stat_re.match("{}".format(div))
        if match is not None:
            stat = match[1]
            value = float(match[2])
            if stat == "Energy":
                value = round(value * bot_eng / 100)
            elif stat == "Nerve":
                value = round(value * bot_nerve / 100)
            elif stat == "Happy":
                value = round(value * bot_hap / 100)
            elif stat == "Life":
                value = round(value * bot_life / 100)
            item_data[stat] = value
            # print('{}: {}'.format(stat, value))

    print(item_data)
    return item_data


def get_vehicle_stats(vehicle_number):
    br.open('https://www.zapoco.com/vehicle/{}'.format(vehicle_number))

    vehicle_data = {}


# inventory parser: returns a dict with all items in inventory of the currently logged in player
def parse_inventory():
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
def get_land_counts():
    br.open('https://www.zapoco.com/land')

    unowned = 0
    owned_grain = 0
    owned_building = 0

    acre_re = re.compile(r'<ellipse class="acre.*" cx=".*" cy=".*" fill="#(.*)" id="acre-(\d+)" rx=".*" ry=".*"></ellipse>')
    acre_divs = br.select('ellipse.acre')

    for div in acre_divs:
        match = acre_re.match('{}'.format(div))

        if match is not None:
            acre_id = int(match[2])
            colour = match[1]
            if colour == "ba8a5e":  # orange
                owned_grain += 1
            elif colour == "07a0ef":  # blue
                owned_building += 1
            elif colour == "6c6c6c":  # grey
                unowned += 1

    return {'unowned': unowned, "owned_grain": owned_grain, "owned_building": owned_building, "total_owned": owned_grain+owned_building, "total": unowned+owned_grain+owned_building}


def get_land_stats(browser, acre_number):
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


async def update_lands_db():
    channel = client.get_channel(ini.DEV_CHANNEL_ID)
    await client.wait_until_ready()
    land = get_land_counts()
    sql = "INSERT INTO `land` (`unowned`, `owned_farm`, `owned_building`, `total_owned`, `total`, `timestamp`) VALUES (%s, %s, %s, %s, %s, %s);"
    db = conn.cursor()
    db.execute(sql, (land['unowned'], land['owned_grain'], land['owned_building'], land['total_owned'], land['total'], datetime.datetime.utcnow()))
    conn.commit()
    print(timestamp + ': Updated land ownership tables in omnidb.')
    db.close()
    await client.send_message(channel, 'Updated land ownership tables in omnidb.')
    asyncio.sleep(3600)


async def run_trackers():
    await get_grain_price() and await get_npc_health() and await update_lands_db()

