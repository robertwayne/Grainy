from discord.ext import commands
from discord.configuration import config as ini
import asyncio
import datetime


bot = commands.Bot(command_prefix='!')
# allows us to override the internal help command
bot.remove_command('help')

dt = datetime.datetime.utcnow()


@bot.event
async def on_message(message):
    # prevent the bot from replying to itself
    if message.author == bot.user:
        return

    # recognizes decorated functions as commands
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' [' + bot.user.id + ']')
    print('-----------------------------------------')
    print(str(dt) + ': Running...')


def main():
    bot.run(ini.BOT_TOKEN)


if __name__ == '__main__':
    main()
