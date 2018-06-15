import asyncio
import sys
import os
import json
import discord
from OmniBot import Configuration as ini
from OmniBot.Client import client
from OmniBot.Trackers import parse_inventory, get_land_stats
from OmniBot.GrainBot import client
from discord.ext import commands


async def reload_bot():
    python = sys.executable
    await asyncio.sleep(1)
    os.execl(python, python, *sys.argv)


async def write_inventory():
    inventory = await parse_inventory()
    r = json.dumps(inventory, sort_keys=True, indent=4)
    # lol, I'm sure this can be done with a loop
    i = r.replace('"', '')
    j = i.replace('}', '')
    k = j.replace('{', '')
    p = k.replace(',', '')
    return p


@client.event
async def on_message(message):
    # prevent self-replies
    if message.author == client.user:
        return

    await client.process_commands(message)


@client.command()
async def test():
    await client.say('Test')


@client.command()
async def stash():
    inv = await write_inventory()
    em = discord.Embed(title="ThePad [7445]",
                       url="https://www.zapoco.com/user/7445",
                       color=0x783e8e)
    await client.say(inv, embed=em)


@client.command()
async def restart(ctx):
    channel = client.get_channel('{cha}'.format(cha=ini.OMNIBOT_CHANNEL_ID))
    if "{eid}".format(eid=ini.ELEVATED_ROLE_ID) in [role.id for role in client.message.author.roles]:
        await client.send_message(channel, 'Restarting now!')
        print('Restarting...')
        await reload_bot()
    else:
        await client.say('You do not have permission to use this command.')
        return


@client.command(pass_context=True)
async def help(ctx):
    channel = ctx.message.author

    em = discord.Embed(title="OmniBot Help",
                       color=0x783e8e)
    em.add_field(name='!stash', value='Displays items in the safehouse stash.',inline=False)
    em.add_field(name='!item <item_#>', value='Displays the stats of an in-game item.', inline=False)
    em.add_field(name='!restart', value='allows an elevated user to restart me.', inline=False)

    await client.say(embed=em)
