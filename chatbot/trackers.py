from databot.database import conn
import asyncio
import discord
import datetime
from chatbot.client import bot
import config.configuration as ini

db = conn.cursor()


async def grain_alerts():
    previous_price = 0

    while True:
        await asyncio.sleep(ini.UPDATE_RATE)
        db.execute("SELECT `current_price` FROM `grain`")
        price = db.fetchone()
        p = int(price['current_price'])
        if p == ini.EVERYONE_ALERT_THRESHOLD and previous_price != price:
            print(str(datetime.datetime.utcnow()) + ': ' + 'Grain Price: ' + str(p))
            em = discord.Embed(title="Grain Alert",
                               url="{}".format(ini.LAND_URL),
                               description="**Price: " + str(p) + "**",
                               color=0x783e8e,
                               timestamp=datetime.datetime.utcnow())
            await bot.send_message(bot.get_channel(ini.OMNIBOT_CHANNEL_ID), '@everyone', embed=em)
            previous_price = price
        elif int(price['current_price']) > ini.ALERT_THRESHOLD and previous_price != price:
            print(str(datetime.datetime.utcnow()) + ': ' + 'Grain Price: ' + str(p))
            em = discord.Embed(title="Grain Alert",
                               url="{}".format(ini.LAND_URL),
                               description="**Price: " + str(p) + "**",
                               color=0x783e8e,
                               timestamp=datetime.datetime.utcnow())
            await bot.send_message(bot.get_channel(ini.OMNIBOT_CHANNEL_ID), embed=em)
            previous_price = price
        conn.commit()


async def db_get_land_stats():
    db.execute("SELECT * FROM `land` WHERE timestamp=(SELECT MAX(timestamp) FROM `land`)")
    stats = db.fetchone()
    conn.commit()

    return stats


async def db_get_item_stats(x):
    sql = "SELECT * FROM `items` WHERE id=%s"
    db.execute(sql, x)
    stats = db.fetchone()
    conn.commit()

    return stats


async def db_get_item_stats_from_name(x):
    sql = "SELECT * FROM `items` WHERE MATCH (Name) AGAINST (%s)"
    db.execute(sql, x)
    stats = db.fetchone()
    conn.commit()

    return stats


async def db_get_vehicle_stats(x):
    sql = "SELECT * FROM `vehicles` WHERE id=%s"
    db.execute(sql, x)
    stats = db.fetchone()
    conn.commit()

    return stats
