#!/usr/bin/python
from gevent import monkey; monkey.patch_socket()
import Configuration
import discord
import asyncio
from Client import client
import Commands
import Trackers

ini = Configuration


@client.event
async def on_member_join(member):
    # rewrite this to use config file and role ID's
    role_new = discord.utils.get(member.server.roles, name="Fresh Faces / Outsiders")
    role_hide = discord.utils.get(member.server.roles, name="Frank’s Little Beauties")
    try:
        await client.add_roles(member, role_new)
    finally:
        await client.add_roles(member, role_hide)


@client.event
@asyncio.coroutine
async def on_ready():
    print('Logged in as ' + client.user.name + ' (' + client.user.id + ')')
    print('-----------------------------------------')
    print('Tracking all sorts of shit...')
    # this needs to be rewritten asynchronously... source of crash
    client.loop.create_task(Trackers.run_trackers())

try:
    client.run(ini.BOT_TOKEN)
finally:
    client.loop.close()
