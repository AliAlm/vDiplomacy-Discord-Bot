
import requests
from lxml import html

page = requests.get('https://vdiplomacy.com/board.php?gameID=41931')
tree = html.fromstring(page.content)

player1 = tree.xpath('/html/body/div[7]/div[2]/div[2]/table/tbody/tr[2]/td[1]/span/span[2]')

print(player1)