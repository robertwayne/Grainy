from gevent import monkey; monkey.patch_socket()
import grequests
import asyncio
from robobrowser import RoboBrowser
import discord
import Configuration
import re

# Create Discord client session
client = discord.Client()

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




async def refresh_config():
    return


async def get_grain_price():
    channel = client.get_channel('{cha}'.format(cha=Configuration.CHANNEL_ID))
    previous_price = 0

    # build the embed
    # discord.Embed(title="Grain Alert", url="https://www.zapoco.com/land/grain", description="Grain Price: " + r)

    while not client.is_closed:
        await asyncio.sleep(Configuration.UPDATE_RATE)
        br.open('{url}'.format(url=Configuration.LAND_URL))
        result = br.find('h2', {'class': '{pcs}'.format(pcs=Configuration.PRICE_CSS_SELECTOR)}).get_text()

        # replace 'result' commas with whitespace and convert to a float
        r = result.replace(',', '')
        price = (float(r))

        if price > Configuration.EVERYONE_ALERT_THRESHOLD:
            print('@everyone Grain Price: ' + r)
            await client.send_message(channel, '@everyone Grain Price: ' + r + ' Sell: <https://www.zapoco.com/land/grain>')
            previous_price = r
        elif price > Configuration.ALERT_THRESHOLD and previous_price != r:
            print('Grain Price: ' + r)
            #await client.send_message(channel, 'Grain Price: ' + r + ' Sell: <https://www.zapoco.com/land/grain>')
            discord.Embed(title="Grain Alert", url="https://www.zapoco.com/land/grain",
                                description="Price: " + r, color=0xff211c)
            previous_price = r
            await asyncio.sleep(Configuration.UPDATE_RATE)


async def get_npc_health():
    channel = client.get_channel('448572817357799454')
    previous_mech_hp = '570/570'
    previous_guard_hp = '670/670'

    while not client.is_closed:
        await asyncio.sleep(1800)
        br.open('https://www.zapoco.com/user/4')
        guard_hp = br.find(string=re.compile('670'))
        br.open('https://www.zapoco.com/user/1220')
        mech_hp = br.find(string=re.compile('570'))

        if guard_hp != '670/670' or mech_hp != '570/570':
            if guard_hp != '670/670' and guard_hp <= previous_guard_hp:
                print('Guard Health: ' + guard_hp)
                await client.send_message(channel, 'The Guard has been attacked! Current health: ' + guard_hp)
                previous_guard_hp = guard_hp
            elif mech_hp != '570/570' and mech_hp <= previous_mech_hp:
                print('Mechanic Health:' + mech_hp)
                await client.send_message(channel, 'The Mechanic has been attacked! Current health: ' + mech_hp)
                previous_mech_hp = mech_hp
        await asyncio.sleep(1800)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (' + client.user.id + ')')
    print('------')
    print('Tracking grain...')
    client.loop.create_task(get_grain_price())
    client.loop.create_task(get_npc_health())

try:
    client.run(Configuration.BOT_TOKEN)
finally:
    client.loop.close()
