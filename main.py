import requests, os, datetime
from lxml import html
from dotenv import load_dotenv
from discord.ext import commands, timers

# Load Token and Server name from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = int(os.getenv('DISCORD_CHANNEL'))

# Player Names
PLAYER1 = os.getenv("PLAYER1")
PLAYER2 = os.getenv("PLAYER2")
PLAYER3 = os.getenv("PLAYER3")
PLAYER4 = os.getenv("PLAYER4")
PLAYER5 = os.getenv("PLAYER5")
PLAYER6 = os.getenv("PLAYER6")

# IDs to names used for mentions
PLAYER1_ID = os.getenv('PLAYER1_ID')
PLAYER2_ID = os.getenv('PLAYER2_ID')
PLAYER3_ID = os.getenv('PLAYER3_ID')
PLAYER4_ID = os.getenv('PLAYER4_ID')
PLAYER5_ID = os.getenv('PLAYER5_ID')
PLAYER6_ID = os.getenv('PLAYER6_ID')

# Country Names (needed to link player name to country)
COUNTRY1 = os.getenv('COUNTRY1')
COUNTRY2 = os.getenv('COUNTRY2')
COUNTRY3 = os.getenv('COUNTRY3')
COUNTRY4 = os.getenv('COUNTRY4')
COUNTRY5 = os.getenv('COUNTRY5')
COUNTRY6 = os.getenv('COUNTRY6')

# Clock
HOUR = 3600
MINUTES = 60


# Refresh page grab
def get_page():
    # Grab page and parse to string
    print("Grabbing page...")
    page_string = requests.get('https://vdiplomacy.com/board.php?gameID=41931')
    page_tree = html.fromstring(page_string.content)
    return page_tree


def get_non_submit(page_ns):
    # Get list of players that haven't submitted orders(by checking icon title)
    print("Getting list of players who haven't submitted.")
    non_submit = page_ns.xpath('//img[@title="No orders submitted!"]')
    non_submit_countries = []
    players_to_country_ns = players_to_country(page_ns)
    # Loop matches up non-submitters with their dictionary equivalent
    for child in non_submit:
        country = child.getparent().getparent()
        country_num = country[1].attrib
        q = country_num['class']
        non_submit_countries.append(players_to_country_ns[f'{q}'])
    print(*non_submit_countries)
    return non_submit_countries


def get_non_ready(page_nr):
    # Get list of players that haven't clicked ready (by checking icon title)
    print("Getting list of players who aren't ready.")
    non_ready = page_nr.xpath('//img[@title="Orders completed, but not ready for next turn"]')
    non_ready_countries = []
    players_to_country_nr = players_to_country(page_nr)
    # Loop matches up non-submitters with their dictionary equivalent
    for child in non_ready:
        country = child.getparent().getparent()
        country_num = country[1].attrib
        q = country_num['class']
        non_ready_countries.append(players_to_country_nr[f'{q}'])
    if non_ready_countries:
        print(*non_ready_countries)
    return non_ready_countries


# Gets remaining time from page
def get_time(page_time):
    print("Getting time remaining...")

    time_remaining_unix = page_time.xpath('//span[@class="timeremaining"]/@unixtime')
    time_remaining_unix = int(time_remaining_unix[0])

    current_time = datetime.datetime
    current_time = current_time.utcnow()

    deadline = datetime.datetime
    deadline = deadline.utcfromtimestamp(time_remaining_unix)

    seconds_left = deadline - current_time

    hours_left = int(int(seconds_left.seconds) / HOUR)
    minutes_left = int((int(seconds_left.seconds) % HOUR) / MINUTES)

    print(f"There are {hours_left} hours and {minutes_left} minutes left.")

    return hours_left, minutes_left


def check_time(time_remaining_int):
    print("Checking time...")

    if time_remaining_int < 3:
        return True
    else:
        return False


def get_daily_message(non_submit_countries, non_ready_countries, time_remaining_hour, time_remaining_min,
                      all_ready=False,
                      final=False):
    print("Getting daily message...")

    daily_message = f"Hello! Orders are due in {time_remaining_hour} hours and {time_remaining_min} minutes."

    if non_submit_countries:
        daily_message = daily_message + "\nPlayers who haven't submitted:\n"
        for name in non_submit_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")
    if non_ready_countries:
        daily_message = daily_message + f"\nPlayers who haven't clicked ready:\n "
        for name in non_ready_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")

    if all_ready:
        daily_message = f"Hello! Everyone has submitted orders, but not all players are ready.\n Orders due in {time_remaining_hour} hours. "
        daily_message = daily_message + "\nPlayers who haven't clicked ready:\n"
        for name in non_ready_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")
    if final:
        daily_message = f"Hello! This is the final warning. Orders are due in {time_remaining_hour} hours."
        daily_message = daily_message + "\nPlayers who haven't submitted:\n"
        for name in non_submit_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")

    daily_message = daily_message + "\nhttps://vdiplomacy.com/board.php?gameID=41931"
    print(daily_message)
    return daily_message


def players_to_country(page_player):
    # Create dictionary linking player to country
    players_to_country = {
        'country1  memberStatusPlaying': page_player.xpath('//span[@class="country1  memberStatusPlaying"]/text()'),
        'country2  memberStatusPlaying': page_player.xpath('//span[@class="country2  memberStatusPlaying"]/text()'),
        'country3  memberStatusPlaying': page_player.xpath('//span[@class="country3  memberStatusPlaying"]/text()'),
        'country4  memberStatusPlaying': page_player.xpath('//span[@class="country4  memberStatusPlaying"]/text()'),
        'country5  memberStatusPlaying': page_player.xpath('//span[@class="country5  memberStatusPlaying"]/text()'),
        'country6  memberStatusPlaying': page_player.xpath('//span[@class="country6  memberStatusPlaying"]/text()')}
    return players_to_country


# Channel ID
channel_id = CHANNEL

# Create dictionary linking person's Discord ID/name with player
names = {
    f"['{COUNTRY1}']": f"{PLAYER1} {PLAYER1_ID} - {COUNTRY1}",
    f"['{COUNTRY2}']": f"{PLAYER2} {PLAYER2_ID} - {COUNTRY2}",
    f"['{COUNTRY3}']": f"{PLAYER3} {PLAYER3_ID} - {COUNTRY3}",
    f"['{COUNTRY4}']": f"{PLAYER4} {PLAYER4_ID} - {COUNTRY4}",
    f"['{COUNTRY5}']": f"{PLAYER5} {PLAYER5_ID} - {COUNTRY5}",
    f"['{COUNTRY6}']": f"{PLAYER6} {PLAYER6_ID} - {COUNTRY6}"

}

# Initialize Client
bot = commands.Bot(command_prefix='$', description='vDiplomacy Discord Bot')
bot.timer_manager = timers.TimerManager(bot)


async def run():
    print("Running...")

    channel_run = bot.get_channel(channel_id)
    page_run = get_page()
    non_submit_countries = get_non_submit(page_run)
    non_ready_countries = get_non_ready(page_run)
    time_remaining_hr, time_remaining_min = get_time(page_run)

    if check_time(time_remaining_hr):
        print("Less than 3 hours remaining. Sending message.\n")

        await channel_run.send(
            get_daily_message(non_submit_countries, non_ready_countries, time_remaining_hr, time_remaining_min))
        bot.timer_manager.create_timer("final", 5400)
    else:
        if not non_submit_countries and non_ready_countries:
            await channel_run.send(
                get_daily_message(non_submit_countries, non_ready_countries, time_remaining_hr, time_remaining_min,
                                  all_ready=True))
        time_remaining_new = time_remaining_hr - 3
        time_remaining_sec = int(3600 * time_remaining_new)
        print(f"More than 3 hours remaining. Waiting {time_remaining_new} hours and checking again.\n")
        bot.timer_manager.create_timer("wait", time_remaining_sec)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    await run()


@bot.event
async def on_wait():
    print("Timer up, wait called, running again...")

    await run()


@bot.event
async def on_final():
    print("Timer up, final called...")

    channel_final = bot.get_channel(channel_id)
    page_final = get_page()
    non_submit_countries = get_non_submit(page_final)
    non_ready_countries = get_non_ready(page_final)
    time_remaining_final_hr, time_remaining_final_min = get_time(page_final)

    if check_time(time_remaining_final_hr):
        await channel_final.send(get_daily_message(non_submit_countries, non_ready_countries, time_remaining_final_hr,
                                                   time_remaining_final_min, final=True))
        bot.timer_manager.create_timer("wait", 10800)


@bot.command()
async def refresh(ctx):
    print("\nRefresh requested")

    page_refresh = get_page()
    non_submit_countries = get_non_submit(page_refresh)
    non_ready_countries = get_non_ready(page_refresh)
    time_remaining_refresh_hr, time_remaining_refresh_min = get_time(page_refresh)

    daily_message = get_daily_message(non_submit_countries, non_ready_countries, time_remaining_refresh_hr,
                                      time_remaining_refresh_min)
    if non_submit_countries or non_ready_countries:
        await ctx.send(daily_message)


@bot.command()
async def rerun():
    print("\nRerunning")
    await run()


bot.run(TOKEN)
