import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
# allows us to override the internal help command
bot.remove_command('help')