from gevent import monkey; monkey.patch_socket()
import grequests
import asyncio
from robobrowser import RoboBrowser
import discord
import Configuration

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


async def refresh():
    try:
        Configuration.config.read('config.ini')
        print('Configuration reloaded.')
    except FileNotFoundError:
        print('Cannot read file /config.ini -- make sure it exists.')


async def get_grain_price():
    previous_price = 0

    while not client.is_closed:
        await asyncio.sleep(Configuration.UPDATE_RATE)
        br.open('{url}'.format(url=Configuration.LAND_URL))
        result = br.find('h2', {'class': '{pcs}'.format(pcs=Configuration.PRICE_CSS_SELECTOR)}).get_text()

        # replace 'result' commas with whitespace and convert to a float
        r = result.replace(',', '')
        price = (float(r))
        channel = client.get_channel('{cha}'.format(cha=Configuration.CHANNEL_ID))

        if price > Configuration.EVERYONE_ALERT_THRESHOLD:
            print('@everyone Grain Price: ' + r)
            await client.send_message(channel, '@everyone Grain Price: ' + r)
        elif price > Configuration.ALERT_THRESHOLD and previous_price != r:
            print('Grain Price: ' + r)
            await client.send_message(channel, 'Grain Price: ' + r)
            previous_price = r
            await asyncio.sleep(Configuration.UPDATE_RATE)


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

try:
    client.run(Configuration.BOT_TOKEN)
finally:
    client.loop.close()
