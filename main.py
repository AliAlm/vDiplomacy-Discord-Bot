import requests, discord, os, time, asyncio
from lxml import html
from dotenv import load_dotenv
from discord.ext import commands

# Load Token and Servername from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')


# Refresh page grab
def get_page():
    # Grab page and parse to string
    page = requests.get('https://vdiplomacy.com/board.php?gameID=41931')
    tree = html.fromstring(page.content)
    return tree


tree = get_page()

# Create dictionary linking player to country
players_to_country = {
    'country1  memberStatusPlaying': tree.xpath('//span[@class="country1  memberStatusPlaying"]/text()'),
    'country2  memberStatusPlaying': tree.xpath('//span[@class="country2  memberStatusPlaying"]/text()'),
    'country3  memberStatusPlaying': tree.xpath('//span[@class="country3  memberStatusPlaying"]/text()'),
    'country4  memberStatusPlaying': tree.xpath('//span[@class="country4  memberStatusPlaying"]/text()'),
    'country5  memberStatusPlaying': tree.xpath('//span[@class="country5  memberStatusPlaying"]/text()'),
    'country6  memberStatusPlaying': tree.xpath('//span[@class="country6  memberStatusPlaying"]/text()')}

# IDs to names used for mentions
shiv_id = '<@653705914901200956>'
aidan_id = '<@527586836193738762>'
bred_id = '<@653733260991397950>'
reuben_id = '<@653850758168444928>'
dan_id = '<@608862611102105613>'
ali_id = '<@336317959028998144>'

# Create dictionary linking person's Discord ID/name with player
names = {
    "['Athens']": f"Shiv {shiv_id}",
    "['Byzantium']": f"Aidan {aidan_id}",
    "['Rhodes']": f"Bred {bred_id}",
    "['Macedonia']": f"Reuben {reuben_id}",
    "['Sparta']": f"Dan {dan_id}",
    "['Persia']": f"Ali {ali_id}"

}

# Get list of players that haven't submitted orders(by checking icon title)
non_submit = tree.xpath('//img[@title="No orders submitted!"]')
non_submit_countries = []

# Loop matches up non-submitters with their dictionary equivalent
for child in non_submit:
    country = child.getparent().getparent()
    country_num = country[1].attrib
    q = country_num['class']
    non_submit_countries.append(players_to_country[f'{q}'])


# Gets remaining time from page
def get_time():
    time_tree = get_page()
    time_remaining = time_tree.xpath('//span[@class="timeremaining"]/text()')
    time_remaining = time_remaining[0]
    time_remaining = int(time_remaining[0:2])

    return time_remaining


# Initialize Client
bot = commands.Bot(command_prefix='$', description='vDiplomacy Discord Bot')


def check_time(time_remaining_int):
    if time_remaining_int < 3:
        return True
    else:
        return False


def get_daily_message(time_remaining_daily):
    daily_message = f"Hello! Orders are due in {time_remaining_daily} hours. \nPlayers who haven't submitted:\n"
    for name in non_submit_countries:
        daily_message = daily_message + (names[f"{name}"] + "\n")
    return daily_message


async def run(time_remaining_run, channel_run):
    time_remaining_int = int(time_remaining_run)
    if check_time(time_remaining_int):
        await channel_run.send(get_daily_message(time_remaining_run))
        await asyncio.sleep(3600 * 10)
        await run(get_time())
    else:
        await asyncio.sleep(3600 * (int(time_remaining_run) - 3))
        await run(get_time())


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(652244891132493854)
    await run(get_time(), channel)
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )


@bot.command()
async def refresh(ctx):
    time_remaining_refresh = get_time()
    daily_message = get_daily_message(time_remaining_refresh)
    if non_submit_countries:
        await ctx.send(daily_message)


bot.run(TOKEN)
