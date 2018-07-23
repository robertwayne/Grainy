#!/usr/bin/python
import sys
sys.path.append('../')
import datetime
import discord
import asyncio
from chatbot.client import bot
import config.configuration as ini
import chatbot.commands
from chatbot.commands import reload_bot


@bot.event
async def on_member_join(member):
    # rewrite this to use config file and role ID's
    role_new = discord.utils.get(member.server.roles, name='Outsiders')
    try:
        await bot.add_roles(member, role_new)
    except Exception as e:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID), 'Failed to add {} to Outsiders role. See log for details.'.format(member.mention))
        print(e)
    finally:
        await bot.send_message(bot.get_channel(ini.DEV_CHANNEL_ID), 'Successfully added {} to Outsiders role.'.format(member.mention))
        print('{} joined the server as an Outsider.'.format(member))


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' [' + bot.user.id + ']')
    print('-----------------------------------------')
    print(str(datetime.datetime.utcnow()) + ': Running...')

    await bot.change_presence(game=discord.Game(name='!help | https://omnidb.io'))


async def main():
    # event_loop = asyncio.get_event_loop()
    # try:
        # asyncio.ensure_future(grain_alerts())
    try:
        bot.run(ini.BOT_TOKEN)
    #     # event_loop.run_forever()
    except Exception as e:
        await bot.send_message(ini.DEV_CHANNEL_ID, e)
        reload_bot()
    finally:
        # print('Closing event loop...')
        #     event_loop.close()
        reload_bot()


if __name__ == '__main__':
    main()
