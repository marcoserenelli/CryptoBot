import discord
import json
import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')

client = discord.Client()


@client.event
async def on_ready():
    print('I have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('$'):
        crypto = message.content[1:].upper()

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': crypto,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            jsonResponse = json.loads(response.text)

            status = jsonResponse['status']
            if status['error_code'] != 0:
                await message.channel.send("Crypto not found :rotating_light:")
                return

            data = jsonResponse['data'][crypto]

            cmcRank = str(data['cmc_rank']).title()
            circulatingSupply = data['circulating_supply']
            maxSupply = data['max_supply']

            stringMessage = "Cmc rank: " + cmcRank + "\n" + \
                str(circulatingSupply) + " / " + str(maxSupply).title()

            if isinstance(maxSupply, int):
                percentage = round(circulatingSupply / maxSupply * 20)
                progressBar = ""
                for i in range(percentage):
                    progressBar += "\U00002588"

                for i in range(20 - percentage):
                    progressBar += "\U00002591"
                stringMessage += "\n"
                stringMessage += progressBar

            quote = data['quote']['USD']
            for q in quote:
                addedString = ""
                value = quote[q]
                if q.startswith("percent"):
                    if value >= 0:
                        addedString += ":green_circle:"
                    else:
                        addedString += ":red_circle:"
                addedString += " "
                addedString += q.replace("_",
                                         ' ').replace("percent change", '%').title()
                addedString += ": "

                if not q.startswith("price"):
                    if isinstance(value, float):
                        addedString += str(round(value, 3))
                    else:
                        addedString += str(value)
                else:
                    addedString += str(value)
                stringMessage += "\n"
                stringMessage += addedString

            slug = data['slug']

            embed = discord.Embed(color=discord.Color.blue(), title=slug.replace(
                '-', ' ').title(), url="https://coinmarketcap.com/currencies/" + slug + "/")
            embed.add_field(name=crypto, value=stringMessage)
            embed.set_footer(text="Scammato da CoinMarketCap")

            print("Successfully printed", crypto)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
        if stringMessage:
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Crypto not found")

client.run(DISCORD_API_KEY)
