from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from .api import StocksApi

from discord import Embed

def stocks_embed(symbol, series_data):
    info = (
        ('open',   series_data['1. open']),
        ('high',   series_data['2. high']),
        ('low',    series_data['3. low']),
        ('close',  series_data['4. close']),
        ('volume', series_data['5. volume']),
    )

    embed = Embed(
        title = symbol,
        description = '\n'.join(f'{title}: **{value}**' for title, value in info),
    )

    return embed

class Stocks(Plugin):

    def load(self):
        self.api = StocksApi(self.config.get('api_key'))

    @command(p.string('!stock') + p.bind(p.word, 'symbol'))
    async def stocks(self, message, symbol):
        symbol = symbol.upper()
        results = await self.api.fetch_symbol_intraday(symbol)
        all_series = results['Time Series (1min)']
        last_key = results['Meta Data']['3. Last Refreshed']
        last_series = all_series[last_key]

        await self.send_message(
            message.channel,
            '',
            embed=stocks_embed(symbol, last_series)
        )


