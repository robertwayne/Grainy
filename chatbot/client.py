import sys
sys.path.append('../')
import discord
from discord.ext import commands

bot = discord.ext.commands.Bot(command_prefix='!')
# allows us to override the internal help command
bot.remove_command('help')
