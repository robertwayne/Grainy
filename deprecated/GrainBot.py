#!/usr/bin/python
from gevent import monkey; monkey.patch_socket()
import discord
import asyncio
from deprecated.Client import client
from discord import CrashReport, Trackers, Configuration as ini


@client.event
async def on_member_join(member):
    # rewrite this to use configuration file and role ID's
    role_new = discord.utils.get(member.server.roles, name="Fresh Faces / Outsiders")
    role_hide = discord.utils.get(member.server.roles, name="Frank’s Little Beauties")
    try:
        await client.add_roles(member, role_new)
    finally:
        await client.add_roles(member, role_hide)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (' + client.user.id + ')')
    print('-----------------------------------------')
    print('Running...')
    # this needs to be rewritten asynchronously... source of crash
    await client.change_presence(game=discord.Game(name='Use !help for commands'))
    await CrashReport.send_crash_report()
    try:
        await client.loop.run_until_complete(asyncio.wait(await Trackers.get_grain_price()))
    except Exception as e:
        CrashReport.save_crash_report(e)
        client.reload_bot()
    # loop = asyncio.get_event_loop()
    # tracker = loop.create_task(Trackers.run_trackers())
    # tracker.add_done_callback(results)
    # loop.run_until_complete(tracker)


def main():
    try:
        client.run(ini.BOT_TOKEN)
    except Exception as e:
        CrashReport.save_crash_report(e)
        client.reload_bot()
    finally:
        client.loop.close()


if __name__ == '__main__':
    main()
