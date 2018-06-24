from discord.ext import commands
from chatbot.omnibot import bot
import discord
import asyncio
import sys
import os


# restarts the entire bot script
async def reload_bot():
    python = sys.executable
    await asyncio.sleep(1)
    os.execl(python, python, *sys.argv)


@bot.command()
@commands.has_role('Nightcrawlers')
async def restart():
    await bot.say('Restarting now!')
    print('Restarting...')
    await reload_bot()


@bot.command(pass_context=True)
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

    await bot.say(embed=em)
