import asyncio
import sys
import os
import json
import discord
import Configuration as ini
from discord.ext import commands
from Trackers import parse_inventory, get_item_stats, get_item_name, get_land_counts
from Client import client


async def reload_bot():
    python = sys.executable
    await asyncio.sleep(1)
    os.execl(python, python, *sys.argv)


async def write_inventory():
    inventory = await parse_inventory()
    r = json.dumps(inventory, sort_keys=True, indent=0)
    # lol, I'm sure this can be done with a loop
    i = r.replace('"', '')
    j = i.replace('}', '')
    k = j.replace('{', '')
    p = k.replace(',', '')
    return p


async def write_item(x):
    return get_item_stats(x)


@client.event
async def on_message(message):
    # prevent self-replies
    if message.author == client.user:
        return

    await client.process_commands(message)


@client.command()
async def stash():
    inv = await write_inventory()
    em = discord.Embed(title="ThePad [7445]",
                       url="https://www.zapoco.com/user/7445",
                       color=0x783e8e)
    await client.say(inv, embed=em)


@client.command()
@commands.has_role('Nightcrawlers')
async def restart():
    await client.say('Restarting now!')
    print('Restarting...')
    await reload_bot()


@client.command(pass_context=True)
async def help():
    em = discord.Embed(title="OmniBot Help",
                       color=0x783e8e)
    em.add_field(name='!stash', value='Displays items in the safehouse stash.',inline=False)
    em.add_field(name='!item <item_#>', value='Displays the stats of an in-game item.', inline=False)
    em.add_field(name='!land', value='Displays general land ownership statistics.', inline=False)
    em.add_field(name='!item request <item_#> <quantity>', value='Requests an item from the safehouse. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!item accept <user_id>', value='Allows an elevated user to accept a queued request. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!restart', value='Allows an elevated user to restart me.', inline=False)

    await client.say(embed=em)


# only works on weapons right now
@client.command(pass_context=True)
async def item(ctx, item_num):
    item = get_item_stats(item_num)

    if item:
        name = get_item_name(item_num)
        em = discord.Embed(title=name + ' | ' + item['Type'],
                           url='https://www.zapoco.com/item/{}'.format(item_num),
                           color=0x783e8e)
        em.set_footer(text='Value: ' + str(item['Value']) + ' | Circulation: ' + str(item['Circulation']))
        for stat in item:
            if stat == 'Value':
                pass
            elif stat == 'Type':
                pass
            elif stat == 'Circulation':
                pass
            elif stat == 'Purchasable':
                pass
            elif stat:
                em.add_field(name='{}'.format(stat), value=item[stat], inline=False)
        await client.say(embed=em)
    else:
        await client.say('Item not found.')


@client.command(pass_context=True)
async def land(ctx):
    land = get_land_counts()
    em = discord.Embed(title='Land Stats',
                       color=0x783e8e)
    em.add_field(name='Unowned: ', value=str(land['unowned']))
    em.add_field(name='Owned (Farms): ', value=str(land['owned_grain']))
    em.add_field(name='Owned (Buildings): ', value=str(land['owned_building']))
    em.set_footer(text='Total Owned: ' + str(land['total_owned']) + ' | Total:' + str(land['total']) +
                  ' | Remaining Land: ' + str((land['total']) - land['total_owned']))

    await client.say(embed=em)
