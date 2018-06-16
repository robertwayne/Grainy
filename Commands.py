import asyncio
import sys
import os
import json
import discord
import Configuration as ini
from Trackers import parse_inventory, get_item_stats, get_item_name
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
async def restart():
    if "{eid}".format(eid=ini.ELEVATED_ROLE_ID) in [role.id for role in client.message.author.roles]:
        await client.say('Restarting now!')
        print('Restarting...')
        await reload_bot()
    else:
        await client.say('You do not have permission to use this command.')
        return


@client.command(pass_context=True)
async def help():
    em = discord.Embed(title="OmniBot Help",
                       color=0x783e8e)
    em.add_field(name='!stash', value='Displays items in the safehouse stash.',inline=False)
    em.add_field(name='!item <item_#>', value='Displays the stats of an in-game item.', inline=False)
    em.add_field(name='!item request <item_#> <quantity>', value='Requests an item from the safehouse. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!item accept <user_id>', value='Allows an elevated user to accept a queued request. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!restart', value='Allows an elevated user to restart me.', inline=False)

    await client.say(embed=em)


# only works on weapons right now
@client.command(pass_context=True)
async def item(item_num):
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
            elif stat == 'Purchaseable':
                pass
            elif stat:
                em.add_field(name='{}'.format(stat), value=item[stat], inline=False)
        await client.say(embed=em)
    else:
        await client.say('Item not found.')
