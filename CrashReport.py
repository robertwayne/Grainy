from Client import client
import Configuration as ini
import traceback
import os


async def send_crash_report():
    channel = client.get_channel(ini.DEV_CHANNEL_ID)

    try:
        with open('crash.log', 'r') as file:
            report = file.read().strip()
            # print('Crash report:\n{}'.format(report))
            await client.send_message(channel, 'Crash report:\n{}'.format(report))
        os.remove('crash.log') # remove the log as it's already reported
    except OSError as e:
        # File doesn't exist -> just ignore
        pass


async def save_crash_report(e):
    with open('crash.log', 'w') as file:
        await file.write('{}'.format(e))
        traceback.print_exc(file=file)