import discord
from discord.ext import commands

client = commands.Bot(command_prefix='!')
# allows us to override the internal help command
client.remove_command('help')
