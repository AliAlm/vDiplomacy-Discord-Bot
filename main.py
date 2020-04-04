import requests, os
from lxml import html
from dotenv import load_dotenv
from discord.ext import commands, timers

# Load Token and Servername from .env
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
    page = requests.get('https://vdiplomacy.com/board.php?gameID=41931')
    get_tree = html.fromstring(page.content)
    return get_tree


def get_nonsubmit():
    # Get list of players that haven't submitted orders(by checking icon title)
    tree_ns = get_page()
    non_submit = tree_ns.xpath('//img[@title="No orders submitted!"]')
    non_submit_countries = []
    players_to_country_ns = players_to_country()
    # Loop matches up non-submitters with their dictionary equivalent
    for child in non_submit:
        country = child.getparent().getparent()
        country_num = country[1].attrib
        q = country_num['class']
        non_submit_countries.append(players_to_country_ns[f'{q}'])
    return non_submit_countries


def get_nonready():
    # Get list of players that haven't clicked ready (by checking icon title)
    tree_nr = get_page()
    non_ready = tree_nr.xpath('//img[@title="Orders completed, but not ready for next turn"]')
    non_ready_countries = []
    players_to_country_nr = players_to_country()
    # Loop matches up non-submitters with their dictionary equivalent
    for child in non_ready:
        country = child.getparent().getparent()
        country_num = country[1].attrib
        q = country_num['class']
        non_ready_countries.append(players_to_country_nr[f'{q}'])
    return non_ready_countries


# Gets remaining time from page
def get_time():
    time_tree = get_page()
    time_remaining = time_tree.xpath('//span[@class="timeremaining"]/text()')
    time_remaining = time_remaining[0]

    time_remaining = int(time_remaining[0:2])

    return time_remaining


def check_time():
    time_remaining_int = get_time()
    if time_remaining_int <= 3:
        return True
    else:
        return False


def get_daily_message(all_ready=False):
    time_remaining_hour = get_time()
    non_submit_countries = get_nonsubmit()
    non_ready_countries = get_nonready()

    daily_message = f"Hello! Orders are due in {time_remaining_hour} hours."

    if non_submit_countries:
        daily_message = daily_message + "\nPlayers who haven't submitted:\n\n"
        for name in non_submit_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")
    if non_ready_countries:
        daily_message = daily_message + f"\nPlayers who haven't clicked ready:\n "
        for name in non_ready_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")

    if all_ready:
        daily_message = f"Hello! Everyone has submitted orders, but not all players are ready.\n Orders due in {time_remaining_hour} hours. "
        daily_message = daily_message + "\nPlayers who haven't clicked ready:\n\n"
        for name in non_ready_countries:
            daily_message = daily_message + ("\t - " + names[f'{name}'] + "\n")

    daily_message = daily_message + "\nhttps://vdiplomacy.com/board.php?gameID=41931"
    return daily_message


def players_to_country():
    player_tree = get_page()
    # Create dictionary linking player to country
    players_to_country = {
        'country1  memberStatusPlaying': player_tree.xpath('//span[@class="country1  memberStatusPlaying"]/text()'),
        'country2  memberStatusPlaying': player_tree.xpath('//span[@class="country2  memberStatusPlaying"]/text()'),
        'country3  memberStatusPlaying': player_tree.xpath('//span[@class="country3  memberStatusPlaying"]/text()'),
        'country4  memberStatusPlaying': player_tree.xpath('//span[@class="country4  memberStatusPlaying"]/text()'),
        'country5  memberStatusPlaying': player_tree.xpath('//span[@class="country5  memberStatusPlaying"]/text()'),
        'country6  memberStatusPlaying': player_tree.xpath('//span[@class="country6  memberStatusPlaying"]/text()')}
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
    channel_run = bot.get_channel(channel_id)
    all_non_submit = get_nonsubmit()

    print("Running: Checking hours remaining...")
    print(f"{get_time()} hours till deadline.")

    if check_time():
        print("Less than 3 hours remaining. Sending message and waiting an hour.")
        await channel_run.send(get_daily_message())
        bot.timer_manager.create_timer("wait", HOUR)
    else:
        all_not_ready = get_nonready()
        if not all_non_submit and all_not_ready:
            await channel_run.send(get_daily_message(True))
        time_remaining_sec = HOUR * (get_time() - 3)
        time_remaining = get_time() - 3
        print(f"More than 3 hours remaining. Waiting {time_remaining} hours and checking again.")
        bot.timer_manager.create_timer("wait", time_remaining_sec)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await run()


@bot.command()
async def refresh(ctx):
    print("Refresh requested")
    non_submit_countries = get_nonsubmit()
    daily_message = get_daily_message()
    if non_submit_countries:
        await ctx.send(daily_message)


@bot.event
async def on_wait():
    print("Timer up, running again")
    await run()


bot.run(TOKEN)
