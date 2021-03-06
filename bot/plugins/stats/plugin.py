from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from . import queries as q

from collections import namedtuple
from time import time

from .handlers import GamesTopHandler, GameStatsHandler, GameUserHandler

import asyncio

GamePlayed = namedtuple(
    'GamePlayed',
    ['id', 'author_id', 'name', 'duration', 'created_at']
)

class Stats(Plugin):

    GAME_DUMP_INTERVAL = 60 * 10

    def load(self):
        context = dict(bot=self.bot, plugin=self)

        self.add_web_handlers(
            (r'/stats/games/top', GamesTopHandler, context),
            (r'/stats/games/game', GameStatsHandler, context),
            (r'/stats/games/user/(?P<user_id>\d+)', GameUserHandler, context),
        )

        self.game_times_by_id = dict()

        now = time()

        for server in self.bot.servers:
            for member in server.members:
                if member.game and member.game.name:
                    game_timer = (member.game.name.lower(), now)
                    self.game_times_by_id[member.id] = game_timer

        self.run_async(self.dump_periodically())

    def unload(self):
        self.dump_all()

    async def on_member_update(self, before, after):
        if before.game != after.game:
            self.update_game(after.id, after.game)

    '''
    Commands
    '''

    stats_prefix = p.string('!stats')

    stats_games_prefix = stats_prefix + p.string('games')

    @command(
        stats_games_prefix + p.bind(p.mention, 'user_id'),
        master_only
    )
    async def stats_games(self, message, user_id):
        member = message.server.get_member(str(user_id))
        if member is None:
            return

        # Flush current tracking
        self.update_game(member.id, member.game)

        games = self.top_user_games(user_id)
        top = [(game.name, game.duration) for game in games[:10]]

        if games:
            since = min(map(lambda g: g.created_at, games))
            since_days = int((time() - since.timestamp()) / (3600 * 24))

            response = (
                '{} has played **{}** different games in the last **{}** days '
                'for a total of **{}** seconds\ntop 10:\n{}'
            ).format(
                f.mention(user_id), len(games), since_days,
                sum(map(lambda g: g.duration, games)),
                f.code_block(f.format_sql_rows(top))
            )
        else:
            response = '{} has not played any games yet'.format(f.mention(user_id))

        await self.send_message(
            message.channel,
            response,
            delete_after = 25
        )

    @command(
        stats_games_prefix + p.string('top') + p.bind(p.maybe(p.integer), 'count'),
        master_only
    )
    async def stats_games_top(self, message, count=10):
        data = self.top_games(message.server, count)

        if data:
            await self.send_message(
                message.channel,
                'Most **{}** games played on this server\n{}'
                    .format(len(data), f.code_block(f.format_sql_rows(data))),
                delete_after = 25
            )

    '''
    Details
    '''

    def top_games(self, server, count):
        user_ids = tuple(member.id for member in server.members)

        with self.transaction() as trans:
            trans.execute(q.top_games, dict(
                limit = count,
                authors_id = user_ids
            ))

            return trans.fetchall()

    def top_users(self, game, count):
        with self.transaction() as trans:
            trans.execute(q.top_users, dict(
                name = game,
                limit = count
            ))

            return trans.fetchall()

    def top_user_games(self, user_id):
        with self.transaction() as trans:
            trans.execute(q.author_games, dict(
                author_id = user_id
            ))

            return [GamePlayed(*row) for row in trans.fetchall()]

    def update_game(self, user_id, new_game):
        try:
            game_name, start = self.game_times_by_id[user_id]
            self.add_game_time(user_id, game_name, start)
        except KeyError:
            pass

        if new_game and new_game.name:
            self.game_times_by_id[user_id] = (new_game.name.lower(), time())
        else:
            self.game_times_by_id.pop(user_id, None)

    def add_game_time(self, user_id, game_name, start):
        duration = int(time() - start)

        with self.transaction() as trans:
            trans.execute(q.add_game_times(1), [(user_id, game_name, duration)])

    def dump_all(self):
        now = time()

        data = [
            (user_id, game_name, now - start) for
            user_id, (game_name, start) in self.game_times_by_id.items()
        ]

        with self.transaction() as trans:
            trans.execute(q.add_game_times(len(data)), data)

        for user_id, (game_name, start) in self.game_times_by_id.items():
            self.game_times_by_id[user_id] = (game_name, now)

    async def dump_periodically(self):
        while True:
            await asyncio.sleep(Stats.GAME_DUMP_INTERVAL)
            self.dump_all()
