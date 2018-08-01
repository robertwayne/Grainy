import sys
sys.path.append('../')
from discord.ext import commands
from chatbot.client import bot
import discord
import sys
import os
import random
from chatbot.trackers import *
from databot.omnispider import *

# GLOBAL VARIABLES
mute_list = []


@bot.event
async def on_message(message):
    # prevent the bot from replying to itself
    if message.author == bot.user:
        return

    # recognizes decorated functions as commands
    await bot.process_commands(message)


async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    errors = {commands.CheckFailure: 'You do not have permission to run this command.',
              commands.NoPrivateMessage: 'You cannot use commands outside the server.'}

    for type, text in errors.items():
        if isinstance(error, type):
            return await bot.say(errors[type])


# restarts the entire bot script
def reload_bot():
    python = sys.executable
    os.execl(python, python, *sys.argv)


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def restart(ctx):
    await bot.say('Restarting now!')
    await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID), '{} executed !restart.'.format(ctx.message.author))
    print('Restarting...')
    reload_bot()


@bot.command(pass_context=True, no_pm=True)
async def help(ctx, x=None):
    em = discord.Embed(title='OmniBot Help',
                       color=0x783e8e,
                       url='https://omnidb.io/#')
    if x == 'db':
        em.add_field(name='!db_force_update_table <items | land | vehicles | NPC>',
                     value='Runs an update function for the relevant table; parses old data, does not add new data.',
                     inline=False)
        em.add_field(name='!db_force_write_new_table <items | land | vehicles | NPC>',
                     value='Writes in new data to the relevant table; does not rewrite current data.',
                     inline=False)
        em.add_field(name='!db_force_run_backup',
                     value='Saves a backup of the entire database in ../DB_BACKUP/',
                     inline=False)
        em.add_field(name='!db_force_delete_table <items | land | vehicles | NPC>',
                     value='Saves a backup of the relevant table data to ../DB_BACKUP/, then deletes it.',
                     inline=False)
        em.add_field(name='!unfuck',
                     value='Loads a DB backup of role permissions. [WARNING: Only use this if someone messes up permissions badly.]',
                     inline=False)
        em.set_footer(text='You must be in a DB-ADMIN role or higher to use these commands.')
        await bot.say(embed=em)
    elif x == 'mod':
        em.add_field(name='!restart',
                     value='Restarts the script.',
                     inline=False)
        em.add_field(name='!mute <user>',
                     value='Toggles a users chat permissions.',
                     inline=False)
        em.add_field(name='!ban <user>',
                     value='Bans the user from the server.',
                     inline=False)
        em.add_field(name='!kick <user>',
                     value='Kicks the user from the server.',
                     inline=False)
        em.set_footer(text='You must be in a MODERATOR role or higher to use these commands.')
        await bot.say(embed=em)
    else:
        em.add_field(name='!item "item name / id" [amount]',
                     value='Displays the stats of an in-game item. Use quotes "" for multiple words.',
                     inline=False)
        em.add_field(name='!vehicle "name" or id',
                     value='Displays the stats of an in-game vehicle.',
                     inline=False)
        em.add_field(name='!compare "item name" or id "item name or id"',
                     value='Compares two weapons or specials stats side-by-side.\nBETA: Modifiers: -daily (24 hour efficiency), -weekly(7 day efficiency)',
                     inline=False)
        em.add_field(name='!land',
                     value='Displays general land ownership statistics.',
                     inline=False)
        em.set_footer(text='Use \'!help mod\' or \'!help db\' for additional commands.')
        await bot.say(embed=em)
    print(str(ctx.message.author) + ' used !help command.')


# noinspection PyShadowingNames
@bot.command(pass_context=True, no_pm=True)
async def land(ctx):
    # noinspection PyShadowingNames
    land = await db_get_land_stats()
    em = discord.Embed(title='Land Stats',
                       color=0x783e8e)
    em.add_field(name='Unowned: ',
                 value=str(land.get('unowned')))
    em.add_field(name='Owned (Farms): ',
                 value=str(land['owned_farm']))
    em.add_field(name='Owned (Buildings): ',
                 value=str(land['owned_building']))
    em.set_footer(text='Total Owned: ' + str(land['total_owned']) + ' | Total:' + str(land['total']) + ' | Last updated: ' + str(land['timestamp']))

    print(str(ctx.message.author) + ' searched for recent land stats')
    await bot.say(embed=em)


@bot.command(pass_context=True, no_pm=True, aliases=['inum', 'i'])
async def item(ctx, x, *, y: int=None):
    # noinspection PyShadowingNames
    try:
        item = await db_get_item_stats_from_name(x)
        if item is None:
            item = await db_get_item_stats(x)
    except TypeError as e:
        print(e)
    finally:
        if item:
            em = discord.Embed(title=item['Name'] + ' [' + str(item['id']) + ']' + ' | ' + item['Type'],
                               url='https://www.zapoco.com/item/{}'.format(item['id']),
                               color=0x783e8e)
            for stat in item:
                if stat == 'Name':
                    pass
                elif stat == 'Value':
                    pass
                elif stat == 'Type':
                    pass
                elif stat == 'Circulation':
                    pass
                elif stat == 'Purchasable':
                    pass
                elif stat == 'Cost':
                    pass
                elif item[stat] is None or item[stat] == 0.0 or item[stat] == 0:
                    pass
                elif stat == 'id':
                    pass
                elif y:
                    if stat == 'Cooldown':
                        em.add_field(name='{}'.format(stat),
                                     value='{}'.format(str(int(item[stat]) * y) + 'm (' + str(int((50 / item[stat]))) + 'x before OD)'),
                                     inline=False)
                        # if stat['Cooldown'] > 50.0:
                        #     em.add_field(name='',
                        #                  value='You will overdose using this many ' + str(x) + '.',
                        #                  inline=False)
                    elif stat:
                        em.add_field(name='{}'.format(stat),
                                     value=str(item[stat] * y),
                                     inline=False)
                        em.set_footer(text='Cost: ' + str(item['Cost'] * y) + ' | These stats are based on using ' + str(y) + ' of this item.')
                elif y is None:
                    if stat == 'Cooldown':
                        em.add_field(name='{}'.format(stat),
                                     value='{}'.format(str(int(item[stat])) + 'm (' + str(int((50 / item[stat]))) + 'x before OD)'),
                                     inline=False)
                    elif stat:
                        em.add_field(name='{}'.format(stat),
                                     value=str(item[stat]),
                                     inline=False)
                        em.set_footer(text='Cost: ' + str(item['Cost']) + ' | Sell Value: ' + str(item['Value']) + ' | Circulation: ' + str(item['Circulation']))
            print(str(ctx.message.author) + ' searched for ' + str(item['Name']))
            await bot.say(embed=em)
        else:
            print(str(ctx.message.author) + ' failed to search for ' + str(x))
            await bot.say('Item not found.')


@bot.command(pass_context=True, no_pm=True, aliases=['c'])
async def compare(ctx, x, y, *, z: str=None):
    try:
        item1 = await db_get_item_stats_from_name(x)
        item2 = await db_get_item_stats_from_name(y)
        try:
            if item1 is None:
                item1 = await db_get_item_stats(x)
        finally:
            if item2 is None:
                item2 = await db_get_item_stats(y)
    except Exception as e:
        print(e)
    finally:
        if item1 and item2:
            if item1['Type'] == 'Weapon' and item2['Type'] == 'Weapon':
                    em = discord.Embed(title=str(item1['Name']) + '  vs  ' + str(item2['Name']),
                                       color=0x783e8e)
                    em.add_field(name='Damage',
                                 value='{}  vs  {}'.format(item1['Damage'], item2['Damage']),
                                 inline=False)
                    em.add_field(name='Accuracy',
                                 value='{}  vs  {}'.format(item1['Accuracy'], item2['Accuracy']),
                                 inline=False)
                    em.add_field(name='Stealth',
                                 value='{}  vs  {}'.format(item1['Stealth'], item2['Stealth']),
                                 inline=False)
                    print(str(ctx.message.author) + ' compared ' + str(item1['Name']) + ' and ' + str(item2['Name']))
                    await bot.say(embed=em)
            elif item1['Type'] == 'Special' and item2['Type'] == 'Special':
                if item1 and item2:
                    energy_cap = 100
                    energy_cap_vip = 150

                    cd1 = int(item1['Cooldown'])
                    cd2 = int(item2['Cooldown'])
                    energy1 = item1['Energy']
                    energy2 = item2['Energy']
                    cost1 = int(item1['Cost'])
                    cost2 = int(item2['Cost'])

                    item1_max_amt_before_od = int((50 / cd1))
                    item2_max_amt_before_od = int((50 / cd2))
                    item1_max_energy_per_use = (item1_max_amt_before_od * energy1)
                    item2_max_energy_per_use = (item2_max_amt_before_od * energy2)
                    item1_cd = (cd1 * item1_max_amt_before_od)
                    item2_cd = (cd2 * item2_max_amt_before_od)
                    item1_max_cost_per_use = int((item1_max_amt_before_od * cost1))
                    item2_max_cost_per_use = int((item2_max_amt_before_od * cost2))

                    em = discord.Embed(title=str(item1['Name']) + '  vs  ' + str(item2['Name']),
                                       color=0x783e8e)
                    em.add_field(name='Energy',
                                 value='{}  vs  {}'.format(item1['Energy'], item2['Energy']),
                                 inline=False)
                    em.add_field(name='Cooldown',
                                 value='{}m  vs  {}m'.format(str(int(item1['Cooldown'])), str(int(item2['Cooldown']))),
                                 inline=False)
                    em.add_field(name='Max Efficiency',
                                 value='{}e per {}m ({}vacs) vs {}e per {}m ({}vacs)'.format(item1_max_energy_per_use, item1_cd, item1_max_cost_per_use, item2_max_energy_per_use, item2_cd, item2_max_cost_per_use),
                                 # value='{}e per {}m ({}vacs)  vs  {}e per {}m ({}vacs)'.format((str(int(item1['Energy'] * e1))), str(int((item1['Cooldown'] * e1))), str(int(e1 * item1['Cost'])), str(int((item2['Energy'] * e2))), str(int((item2['Cooldown'] * e2))), str(int(e2 * item2['Cost']))),
                                 inline=False)
                    if z == '-daily':
                        em.add_field(name='Max Daily Efficiency',
                                     value='{}e at {}vacs vs {}e at {}vacs'.format(item1_max_energy_per_use * (1440 / item1_cd), item1_max_cost_per_use * (1440 / item1_cd), item2_max_energy_per_use * (1440 / item2_cd), item2_max_cost_per_use * (1440 / item2_cd)),
                                     inline=False)
                    # em.add_field(name='Hourly Efficiency',
                    #              value='{}vacs per hour vs {}vacs per hour'.format((item1_max_cost_per_use * (60 / item2_max_amt_per_use)), (item2_max_cost_per_use * (60 / item2_max_amt_per_use))),
                    #              inline=False)
                    print(str(ctx.message.author) + ' compared ' + str(item1['Name']) + ' and ' + str(item2['Name']))
                    await bot.say(embed=em)
        else:
            print(str(ctx.message.author) + ' failed to compare ' + str(x) + ' and ' + str(y))
            await bot.say('Incorrect ID or Names given.')


@bot.command(pass_context=True, no_pm=True, aliases=['v'])
async def vehicle(ctx, x):
    # noinspection PyShadowingNames
    try:
        vehicle = await db_get_vehicle_stats_from_name(x)
        if vehicle is None:
            vehicle = await db_get_vehicle_stats(x)
    except TypeError as e:
        print(e)
    finally:
        if vehicle:
            em = discord.Embed(title=vehicle['Name'] + ' | Vehicle',
                               url='https://www.zapoco.com/vehicle/{}'.format(x),
                               color=0x783e8e)
            for stat in vehicle:
                if stat == 'Name':
                    pass
                elif vehicle[stat] is None:
                    pass
                elif stat == 'id':
                    pass
                elif stat:
                    em.add_field(name='{}'.format(stat),
                                 value=vehicle[stat],
                                 inline=False)
            print(str(ctx.message.author) + ' searched for ' + str(vehicle['Name']))
            await bot.say(embed=em)
        else:
            print(str(ctx.message.author) + ' failed to search for ' + str(x))
            await bot.say('Vehicle not found.')


#####################################
#            MOD COMMANDS           #
#####################################
@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def mute(ctx, user: discord.Member):
    silenced_role = discord.utils.get(ctx.message.author.server.roles, name='SILENCED')
    try:
        if user in mute_list:
            mute_list.remove(user)
            await bot.remove_roles(user, silenced_role)
            await bot.say('{} has been un-muted.'.format(user.name))
        else:
            mute_list.append(user)
            await bot.add_roles(user, silenced_role)
            await bot.say('{} has been muted.'.format(user.name))
    except Exception as e:
        print(e)
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !mute on {}.'.format(ctx.message.author, user.name))


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def kick(ctx, user: discord.Member):
    try:
        if user:
            await bot.kick(user)
            await bot.say('{} has been removed from the server.'.format(user.name))
    except Exception as e:
        print(e)
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !kick on {}.'.format(ctx.message.author, user.name))


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def ban(ctx, user: discord.Member):
    try:
        if user:
            await bot.ban(user)
            await bot.say('{} has been banned from the server.'.format(user.name))
    except Exception as e:
        print(e)
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !ban on {}.'.format(ctx.message.author, user.name))


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def purge(ctx, author):
    return 0


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ELEVATED_ROLE_NAME))
async def sh():
    msg = get_safehouse_respect()
    await bot.say(msg)


#####################################
#         DATABASE COMMANDS         #
#####################################


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ADMIN_ROLE_NAME))
async def db_force_update_table(ctx, x):
    try:
        if x == 'items':
            await db_update_item_table()
            await bot.say('Successfully updated OmniDB.Items')
        elif x == 'land':
            await db_update_land_table()
            await bot.say('Successfully updated OmniDB.Land')
        elif x == 'vehicles':
            await db_update_vehicle_table()
            await bot.say('Successfully updated OmniDB.Vehicles')
        else:
            await bot.say('Invalid parameter.')
    except Exception as e:
        print(e)
        await bot.say('Failed to update. See error log.')
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !dn_force_write_new_table {}.'.format(ctx.message.author, x))


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ADMIN_ROLE_NAME))
async def db_force_write_new_table(ctx, x):
    try:
        if x == 'items':
            await db_write_item_table()
            await bot.say('Successfully added OmniDB.Items')
        elif x == 'land':
            await db_update_land_table()
            await bot.say('Successfully updated OmniDB.Land')
        elif x == 'vehicles':
            await db_write_vehicle_table()
            await bot.say('Successfully added OmniDB.Vehicles')
        else:
            await bot.say('Invalid parameter.')
    except Exception as e:
        print(e)
        await bot.say('Failed to update. See error log.')
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !dn_force_write_new_table {}.'.format(ctx.message.author, x))


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ADMIN_ROLE_NAME))
async def db_search_index():
    sql = "ALTER TABLE `vehicles` ADD FULLTEXT(Name)"
    db.execute(sql)
    conn.commit()
    await bot.say('Added search index table for Omni.Vehicles')


@bot.command(pass_context=True, no_pm=True)
@commands.has_role('{}'.format(ini.ADMIN_ROLE_NAME))
async def db_set_cost(ctx, x, y):
    try:
        await db_update_cost(x, y)
    except Exception as e:
        print(e)
        await bot.say('Failed to update. See error log.')
    finally:
        await bot.say('Successfully updated costs.')
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID),
                               '{} executed !db_set_cost {} {}.'.format(ctx.message.author, x, y))
