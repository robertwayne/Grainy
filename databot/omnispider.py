import sys
sys.path.append('../')
import grequests
from robobrowser import RoboBrowser
import re
import asyncio
import config.configuration as ini
from databot.database import conn
import datetime
import random

# open up a cursor
db = conn.cursor()

# Build a session and submit log-in data upon initialization
headers = {
    "Connection": "keep-alive"
}

session_name = grequests.Session()
session_name.headers = headers

br = RoboBrowser(session=session_name, parser='html.parser', history=True)
br.open('{url}'.format(url=ini.LOGIN_URL))

form = br.get_form()
form['username'] = '{usr}'.format(usr=ini.BOT_USERNAME)
form['password'] = '{pwd}'.format(pwd=ini.BOT_PASSWORD)
try:
    br.submit_form(form)
except SyntaxError:
    print("Form submission failed. Invalid log-in data.")


def create_session():
    # Build a session and submit log-in data upon initialization
    headers = {
        "Connection": "keep-alive"
    }

    session_name = grequests.Session()
    session_name.headers = headers

    br = RoboBrowser(session=session_name, parser='html.parser', history=True)
    br.open('{url}'.format(url=ini.LOGIN_URL))

    form = br.get_form()
    form['username'] = '{usr}'.format(usr=ini.BOT_USERNAME)
    form['password'] = '{pwd}'.format(pwd=ini.BOT_PASSWORD)
    try:
        br.submit_form(form)
    except SyntaxError:
        print("Form submission failed. Invalid log-in data.")

    return br


async def get_grain_price():
    db.execute("SELECT `current_price` FROM `grain`")
    db_price = db.fetchone()
    p1 = int(db_price['current_price'])
    print(p1)

    db.execute("SELECT `previous_price` FROM `grain`")
    test = db.fetchone()
    p2 = int(test['previous_price'])
    print(p2)

    timer = 4
    await asyncio.sleep(timer)

    br = create_session()
    br.open('https://www.zapoco.com/land/grain')
    result = br.find('h2', {'class': 'text-bold text-light space-1'}).get_text()
    # replace 'result' commas with whitespace and convert to an int
    r = result.replace(',', '')
    price = (int(r))
    print('Current Price: ' + str(price))

    return price


async def db_update_grain():
    while True:
        db.execute("UPDATE `grain` SET previous_price=current_price")
        cur_price = await get_grain_price()
        sql = "UPDATE `grain` SET current_price=%s"
        db.execute(sql, cur_price)


def get_item_stats(item_number):
    br.open('https://www.zapoco.com/item/{}'.format(item_number))

    item_data = {}

    # regexes for different types of data
    name_re = re.compile(r'<h2><span class="text-light text-strong">(.*)</span></h2>')
    stat_re = re.compile(r'<div class="col-4 space-2">\s*<p>(\w+)</p>\s*<div class="progress-bar"><div class="progress" style="width:(.*)%"></div>\s*</div>\s*</div>')
    info_re = re.compile(r'<div class="col-3">\s*<h4 class="text-bold text-light">(.*)</h4>\s*<p>(.*)</p>\s*</div>')
    value_re = re.compile(r'<i class="fa fa-medkit"></i>(.*)')
    check_re = re.compile(r'<i class="fa fa-check"></i>')

    # grab the correct html snippets, as strings
    name_div = br.select('h2')  # Name is the first one
    stat_divs = br.select('div.col-4.space-2')
    info_divs = br.select('div.col-3')

    if len(name_div) > 0:
        match = name_re.match("{}".format(name_div[0]))
        if match is not None:
            item_data['Name'] = match[1]

    # print(info_divs)
    for div in info_divs:
        match = info_re.match("{}".format(div))
        if match is not None:
            info = match[2]
            value = match[1]
            if info == "Value":
                value = int(value_re.match(value)[1].replace(',', ''))
            elif info == "Purchasable":
                if check_re.match(value) is None:
                    value = 'Yes'
                else:
                    value = 'No'
            elif info == "In Circulation":
                info = 'Circulation'
                value = int(value.replace(',', ''))

            item_data[info] = value
            # print('{}: {}'.format(info, value))

    # hard coded bot max stats; used for normalization
    bot_eng = 100
    bot_nerve = 10
    bot_hap = 100
    bot_life = 100

    # print(stat_divs)
    for div in stat_divs:
        # print(div)
        match = stat_re.match("{}".format(div))
        if match is not None:
            stat = match[1]
            value = float(match[2])
            if stat == "Energy":
                value = round(value * bot_eng / 100)
            elif stat == "Nerve":
                value = round(value * bot_nerve / 100)
            elif stat == "Happy":
                value = round(value * bot_hap / 100)
            elif stat == "Life":
                value = round(value * bot_life / 100)
            item_data[stat] = value
            # print('{}: {}'.format(stat, value))

    print(item_data)
    return item_data


def get_vehicle_stats(vehicle_number):
    br.open('https://www.zapoco.com/vehicle/{}'.format(vehicle_number))

    veh_data = {}

    # regexes for different types of data
    name_re = re.compile(r'<h2><span class="text-light text-strong">(.*)</span></h2>')
    stat_re = re.compile(r'<div class="col-4">\s*<p>(\w+)</p>\s*<div class="progress-bar"><div class="progress" style="width:(.*)%"></div>\s*</div>\s*</div>')

    # grab the correct html snippets, as strings
    name_div = "{}".format(br.select('h2')[0])  # Name
    stat_divs = br.select('div.col-4')

    veh_data['Name'] = name_re.match(name_div)[1]
    # if len(name_div) > 0:
    #     match = name_re.match("{}")
    #     if match is not None:
    #         veh_data['Name'] = match[1]

    # print(stat_divs)
    for div in stat_divs:
        # print(div)
        match = stat_re.match("{}".format(div))
        if match is not None:
            stat = match[1]
            value = int(match[2])
            if stat == "Speed":
                value = value
            elif stat == "Comfort":
                value = value
            veh_data[stat] = value
            # print('{}: {}'.format(stat, value))

    print(veh_data)
    return veh_data


# inventory parser: returns a dict with all items in inventory of the currently logged in player
def parse_inventory():
    br.open('https://www.zapoco.com/inventory')
    item_re = re.compile(r'<div class="pull-left pd-h-sm">\s*<a class="text-light text-strong" '
                         r'href="https://www.zapoco.com/item/(\d+)">(.*)</a> x(\d+)\s*</div>')

    selection = br.select('div.pull-left.pd-h-sm')

    inventory = {}

    for div in selection:
        # match item name, amount
        # no match -> no item
        match = item_re.match('{}'.format(div))
        if match is not None:
            item_number = match[1]
            item = match[2]
            count = match[3]
            inventory[item] = count  # item's can't be listed twice so we don't have to check for duplicates

    print(inventory)
    return inventory


# land scraping code
def get_land_counts():
    br.open('https://www.zapoco.com/land')

    unowned = 0
    owned_grain = 0
    owned_building = 0

    acre_re = re.compile(r'<ellipse class="acre.*" cx=".*" cy=".*" fill="#(.*)" id="acre-(\d+)" rx=".*" ry=".*"></ellipse>')
    acre_divs = br.select('ellipse.acre')

    for div in acre_divs:
        match = acre_re.match('{}'.format(div))

        if match is not None:
            acre_id = int(match[2])
            colour = match[1]
            if colour == "ba8a5e":  # orange
                owned_grain += 1
            elif colour == "07a0ef":  # blue
                owned_building += 1
            elif colour == "6c6c6c":  # grey
                unowned += 1

    return {'unowned': unowned, "owned_grain": owned_grain, "owned_building": owned_building, "total_owned": owned_grain+owned_building, "total": unowned+owned_grain+owned_building}


#####################################
#      DATABASE WRITE FUNCTIONS     #
#####################################


async def db_write_vehicle_table():
    try:
        db.execute("SELECT COUNT(*) FROM vehicles")
        id_last = db.fetchone()
        for x in range(id_last['COUNT(*)'], 10000):
            vehicle = get_vehicle_stats(x)
            if vehicle['Name'] is None:
                break
            else:
                sql = "INSERT INTO `vehicles` (`name`, `distance`, `speed`, `comfort`, `id`) VALUES (%s, %s, %s, %s, %s)"
                db.execute(sql, (vehicle.get('Name'), vehicle.get('Distance'), vehicle.get('Speed'), vehicle.get('Comfort'), x))
                conn.commit()
    except Exception as e:
        print(e)
        pass
    finally:
        print('Success.')


async def db_write_item_table():
    try:
        # count rows in items table, then add from there
        db.execute("SELECT COUNT(*) FROM items")
        id_last = db.fetchone()
        # this is hacky as fuck: returns dict w/ COUNT(*) as key
        for x in range(id_last['COUNT(*)'], 10000):
            item = get_item_stats(x)
            # every item has to have a name, so this ensures we break out when we reach the end of items in game
            if item['Name'] is None:
                break
            else:
                sql = "INSERT INTO `items` (`Name`, `Type`, `Value`, `Circulation`, `Damage`, `Accuracy`, `Stealth`, `Cooldown`, `Life`, `Happiness`, `Energy`, `Nerve`, `id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                db.execute(sql, (item.get('Name', None), item.get('Type', None), item.get('Value', None),
                                 item.get('Circulation', None), item.get('Damage', None), item.get('Accuracy', None), item.get('Stealth', None),
                                 item.get('Cooldown', None), item.get('Life', None), item.get('Happy', None), item.get('Energy', None),
                                 item.get('Nerve', None), x))
                conn.commit()
    except Exception as e:
        print(e)
        pass
    finally:
        print('Success.')


async def db_update_land_table():
    try:
        land = get_land_counts()
        sql = "INSERT INTO `land` (`unowned`, `owned_farm`, `owned_building`, `total_owned`, `total`, `timestamp`) VALUES (%s, %s, %s, %s, %s, %s);"
        db.execute(sql, (land['unowned'], land['owned_grain'], land['owned_building'], land['total_owned'], land['total'], datetime.datetime.utcnow()))
        conn.commit()
    except Exception as e:
        print(e)
        pass
    finally:
        print('Success.')


#####################################
#      DATABASE UPDATE FUNCTIONS    #
#####################################


async def db_update_item_table():
    try:
        limit = db.execute("SELECT COUNT(*) FROM items")
        conn.commit()
        for x in range(1, limit):
            sql = "UPDATE items SET Name=%s, Type=%s, Value=%s, Circulation=%s, Damage=%s, Accuracy=%s, Stealth=%s, Cooldown=%s, Life=%s, Happiness=%s, Energy=%s, Nerve=%s WHERE id=%s"
            item = get_item_stats(x)
            db.execute(sql, (item.get('Name', None), item.get('Type', None), item.get('Value', None),
                             item.get('Circulation', None), item.get('Damage', None), item.get('Accuracy', None),
                             item.get('Stealth', None),
                             item.get('Cooldown', None), item.get('Life', None), item.get('Happy', None),
                             item.get('Energy', None),
                             item.get('Nerve', None), x))
            conn.commit()
    except Exception as e:
        print(e)
        pass
    finally:
        print('Success.')


async def db_update_cost(x, y):
    try:
        db.execute("SELECT Name, Cost FROM items")
        sql = "UPDATE items SET Cost=%s WHERE Name=%s"
        db.execute(sql, (y, x))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        print('Success')


async def db_update_vehicle_table():
    try:
        for x in range(1, 10):
            sql = "UPDATE vehicles SET name=%s, distance=%s, speed=%s, comfort=%s WHERE id=%s"
            vehicle = get_vehicle_stats(x)
            db.execute(sql, (vehicle.get('Name', None), vehicle.get('Distance', None), vehicle.get('Speed', None), vehicle.get('Comfort', None), x))
            conn.commit()
    except Exception as e:
        print(e)
        pass
    finally:
        print('Success.')


def main():
    event_loop = asyncio.get_event_loop()
    try:
        print('Running...')
        asyncio.ensure_future(db_update_grain())
        event_loop.run_forever()
    except Exception as e:
        print(e)
    finally:
        print('Closing database...')
        db.close()
        print('Closing event loop...')
        event_loop.close()


if __name__ == '__main__':
    main()
