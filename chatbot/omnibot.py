#!/usr/bin/python
import datetime
import discord
import asyncio
from chatbot.client import bot
import config.configuration as ini
from chatbot.trackers import grain_alerts
import chatbot.commands


@bot.event
async def on_member_join(member):
    # rewrite this to use config file and role ID's
    role_new = discord.utils.get(member.server.roles, name="Fresh Faces / Outsiders")
    await bot.add_roles(member, role_new)


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' [' + bot.user.id + ']')
    print('-----------------------------------------')
    print(str(datetime.datetime.utcnow()) + ': Running...')

    await bot.change_presence(game=discord.Game(name='!help | https://omnidb.io'))


def main():
    event_loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(grain_alerts())
        bot.run(ini.BOT_TOKEN)
        event_loop.run_forever()
    except Exception as e:
        print(e)
    finally:
        print('Closing event loop...')
        event_loop.close()


if __name__ == '__main__':
    main()
