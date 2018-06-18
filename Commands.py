import asyncio
import sys
import os
import json
import discord
import Configuration as ini
from discord.ext import commands
from Trackers import parse_inventory, get_item_stats, get_item_name, get_land_counts, update_lands_db
from Client import client, timestamp
from Database import conn


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
    em.add_field(name='!vehicle <vehicle_#>', value='Displays the stats of an in-game vehicle.', inline=False)
    em.add_field(name='!land', value='Displays general land ownership statistics.', inline=False)
    em.add_field(name='!item request <item_#> <quantity>', value='Requests an item from the safehouse. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!item accept <user_id>', value='Allows an elevated user to accept a queued request. (NOT IMPLEMENTED)', inline=False)
    em.add_field(name='!restart', value='Allows an elevated user to restart me.', inline=False)

    await client.say(embed=em)


# prints an items statistics to chat
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

# prints a vehicles statistics to chat (WAITING ON GET_VEHICLE_STATS() IMPLEMENTATION)
# @client.command(pass_context=True)
# async def vehicle(ctx, vehicle_num):
#     vehicle = get_vehicle_stats(vehicle_num)
#     name = get_vehicle_name(vehicle_num)
#     if vehicle:
#         em = discord.Embed(title=name + ' | Vehicle',
#                          url='https://www.zapoco.com/vehicle/{}'.format(vehicle_num),
#                          color=0x783e8e)
#         for stat in vehicle:
#             em.add_field(name='{}'.format(stat), value=vehicle[stat], inline=False)
#         await client.say(embed=em)
#     else:
#         await client.say('Vehicle not found.')


@client.command(pass_context=True)
async def land(ctx):
    land = get_land_counts()
    em = discord.Embed(title='Land Stats',
                       color=0x783e8e)
    em.add_field(name='Unowned: ', value=str(land['unowned']))
    em.add_field(name='Owned (Farms): ', value=str(land['owned_grain']))
    em.add_field(name='Owned (Buildings): ', value=str(land['owned_building']))
    em.set_footer(text='Total Owned: ' + str(land['total_owned']) + ' | Total:' + str(land['total']))

    await client.say(embed=em)


@client.command(pass_context=True)
async def landDB(ctx):
    sql = "SELECT "


# @client.command(pass_context=True)
# @commands.has_role('The Brains')
# async def db_parse_items(ctx, i_num):
#     name = get_item_name(i_num)
#     stats = get_item_stats(i_num)
#     j = json.dumps(stats)
#
#     #sql = "INSERT INTO `items` VALUES %s"
#     #db.execute("INSERT INTO `items` VALUES %s;", j)
#
#     sql = "INSERT INTO `items` VALUES %s;"
#     db.execute(sql, (name, j))
#
#
#
#
#     conn.commit()
#     db.close()
#     await client.say('Inserted data into omnidb.')


# Force a land update in the database by calling the update_land_db() function
@client.command(pass_context=True)
@commands.has_role('The Brains')
async def db_write_land(ctx):
    update_lands_db()
