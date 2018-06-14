import asyncio
import sys
import os
import json
import discord
from OmniBot import Configuration as ini
from OmniBot.Client import client
from OmniBot.Trackers import parse_inventory, get_land_stats


async def reload_bot():
    python = sys.executable
    await asyncio.sleep(1)
    os.execl(python, python, *sys.argv)


async def write_inventory():
    inventory = await parse_inventory()
    r = json.dumps(inventory)
    return r


@client.event
async def on_message(message):
    # prevent self-replies
    if message.author == client.user:
        return

    if message.content.startswith('!restart'):
        channel = client.get_channel('{cha}'.format(cha=ini.OMNIBOT_CHANNEL_ID))
        # elevated_roles = ['445929589903065101', '445929835144151050', '454639766567256064', '455129483532566535']
        # uh, iterate through this shit...????
        # add command to grab role ID automatically?
        if "{eid}".format(eid=ini.ELEVATED_ROLE_ID) in [role.id for role in message.author.roles]:
            await client.send_message(channel, 'Restarting now!')
            print('Restarting...')
            await reload_bot()
        else:
            await client.send_message(channel, 'You do not have permission to use this command.')
            return

    if message.content.startswith('!stash'):
        channel = client.get_channel('{cha}'.format(cha=ini.DEV_CHANNEL_ID))
        inv = await write_inventory()
        em = discord.Embed(title="The Pad [7445]",
                           url="https://www.zapoco.com/user/7445")
        # NOT FINISHED WORK IN PROGRESS
        await client.send_message(channel, 'JSON OUTPUT: ' + inv)
