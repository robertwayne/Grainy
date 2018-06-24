#!/usr/bin/python
from discord.ext import commands
import datetime
import chatbot.commands
import discord
import asyncio
from chatbot.client import bot
import chatbot.configuration as ini

dt = datetime.datetime.utcnow()


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' [' + bot.user.id + ']')
    print('-----------------------------------------')
    print(str(dt) + ': Running...')


def main():
    bot.run(ini.BOT_TOKEN)


if __name__ == '__main__':
    main()
