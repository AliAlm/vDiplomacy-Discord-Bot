import requests
from lxml import html

page = requests.get('https://vdiplomacy.com/board.php?gameID=41931')
tree = html.fromstring(page.content)

players_to_country = {}

player1 = tree.xpath('//span[@class="country1  memberStatusPlaying"]/text()')
player2 = tree.xpath('//span[@class="country2  memberStatusPlaying"]/text()')
player3 = tree.xpath('//span[@class="country3  memberStatusPlaying"]/text()')
player4 = tree.xpath('//span[@class="country4  memberStatusPlaying"]/text()')
player5 = tree.xpath('//span[@class="country5  memberStatusPlaying"]/text()')
player6 = tree.xpath('//span[@class="country6  memberStatusPlaying"]/text()')

players_to_country['country1  memberStatusPlaying'] = player1
players_to_country['country2  memberStatusPlaying'] = player2
players_to_country['country3  memberStatusPlaying'] = player3
players_to_country['country4  memberStatusPlaying'] = player4
players_to_country['country5  memberStatusPlaying'] = player5
players_to_country['country6  memberStatusPlaying'] = player6

non_submit = tree.xpath('//img[@title="No orders submitted!"]')
non_submit_countries = []

for child in non_submit:
    country = child.getparent().getparent()
    country_num = country[1].attrib
    q = country_num['class']
    non_submit_countries.append(q)
    print(players_to_country[f'{q}'])
