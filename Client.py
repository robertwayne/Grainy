import discord
from discord.ext import commands
import datetime

# Get a timestamp for various debug and data functions
timestamp = datetime.datetime.utcnow()
dt = str(timestamp)

client = commands.Bot(command_prefix='!')
# allows us to override the internal help command
client.remove_command('help')
