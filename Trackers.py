import grequests
import asyncio
import discord
from robobrowser import RoboBrowser
import Configuration
import datetime
import re
from Client import client

ini = Configuration


# Build a session and submit log-in data upon initialization
headers = {
    "Connection": "keep-alive"
}

session = grequests.Session()
session.headers = headers
br = RoboBrowser(session=session, parser='html.parser', history=True)
br.open('{url}'.format(url=Configuration.LOGIN_URL))

form = br.get_form()
form['username'] = '{usr}'.format(usr=Configuration.BOT_USERNAME)
form['password'] = '{pwd}'.format(pwd=Configuration.BOT_PASSWORD)
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

        if guard_hp != '670/670':
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


async def run_trackers():
    await get_grain_price()
    await get_npc_health()
    # await get_rare_items()
