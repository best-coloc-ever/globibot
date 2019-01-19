from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import global_cooldown, user_cooldown, master_only

from . import content
from . import queries as q

from datetime import datetime

ALL_TRIVAS = (
    ('animals', content.AnimalsTrivia),
    ('capitals', content.CapitalsTrivia),
    ('flags', content.FlagsTrivia),
    ('pokemons', content.PokemonsTrivia),
    ('traps', content.TrapsTrivia),
    ('states', content.USStatesTrivia),
    ('games', content.GameReleasesTrivia),
    ('anime', content.AnimesTrivia),
    ('programming', content.ProgrammingTrivia),
)

class Trivia(Plugin):

    def load(self):
        self.trivias = dict()

        for name, Behavior in ALL_TRIVAS:
            try:
                self.trivias[name] = Behavior()
            except Exception as e:
                self.warning('Failed to initialize trivia {}: {}'.format(name, e))

    @command(
        p.string('!trivia') + p.bind(p.word, 'topic') + p.eof,
        global_cooldown(20, True)
    )
    async def trivia(self, message, topic):
        # if message.channel.id == "84822922958487552":
        #     await self.send_message(message.channel, "<#401160296732950564>")
        #     return

        try:
            trivia_gen = self.trivias[topic.lower()]
        except KeyError:
            topics_string = ' '.join(
                '__{}__'.format(name)
                for name in self.trivias.keys()
            )
            await self.send_message(
                message.channel,
                'There is no trivia about __{}__, available topics are: {}\n'
                    .format(topic, topics_string)
            )
        else:
            await self.run_trivia(message.channel, trivia_gen(), topic)

    async def send(self, channel, message):
        sender = self.send_file if 'file_path' in message else self.send_message
        return await sender(channel=channel, **message)

    async def get_answers(self, channel, trivia_message):
        answers = self.bot.logs_from(channel, after=trivia_message, reverse=True)

        users = set()
        unique_answers = list()
        async for answer in answers:
            if answer.author.id in users:
                continue
            if answer.edited_timestamp is not None:
                continue
            unique_answers.append(answer)
            users.add(answer.author.id)

        return sorted(unique_answers, key=lambda m: m.timestamp)

    async def run_trivia(self, channel, trivia, topic):
        premise = next(trivia)
        message = await premise
        trivia_message = await self.send(channel, message)

        query = next(trivia)
        await query()
        answers = await self.get_answers(channel, trivia_message)
        self.debug(['{}: {}'.format(a.author.name, a.clean_content) for a in answers])
        winner, conclusion = trivia.send(answers)

        await self.send(channel, conclusion)

        if winner:
            if len(answers) >= 3:
                self.register_winner(winner, channel.server, topic)
                points = self.get_points(winner.id, channel.server.id)
                await self.send_message(
                    channel,
                    '{} now has {} points!'.format(winner.mention, points)
                )
            else:
                await self.send_message(
                    channel,
                    'Not enough participants to make this one count'
                )

    @command(
        p.string('!trivia') + p.string('stats')
                            + p.bind(p.mention, 'user_id')
                            + p.bind(p.maybe(p.word), 'topic')
    )
    async def trivia_stats(self, message, user_id, topic=None):
        ranks = self.get_ranks(message.server.id, topic)
        for_string = '' if topic is None else ' for `{}`'.format(topic)
        try:
            rank, points = next(
                (i + 1, points)
                for i, (points, id) in enumerate(ranks)
                if id == user_id
            )
        except StopIteration:
            await self.send_message(
                message.channel,
                '{} has no points on this server{}'.format(f.mention(user_id), for_string)
            )
        else:
            await self.send_message(
                message.channel,
                '{} has {} points and is ranked #{} on this server{}'
                    .format(f.mention(user_id), points, rank, for_string)
            )

    @command(
        p.string('!trivia') + p.string('stats')
                            + p.string('all')
                            + p.bind(p.maybe(p.word), 'topic')
    )
    async def trivia_stats_all(self, message, topic=None):
        ranks = self.get_ranks(message.server.id, topic)
        ranks = ranks[:10]

        def user_name(u_id):
            user = self.bot.find_user(str(u_id))
            return user.name if user else '???'

        leaderboard = '\n'.join(
            '#{:>2} {:<30} ({:>3} pts)'.format(i + 1, user_name(user_id), points)
            for i, (points, user_id) in enumerate(ranks)
        )

        for_string = '' if topic is None else ' for `{}`'.format(topic)
        await self.send_message(
            message.channel,
            'Top {} on this server{}:\n{}'.format(
                len(ranks), for_string, f.code_block(leaderboard)
            )
        )


    def register_winner(self, winner, server, topic):
        with self.transaction() as trans:
            trans.execute(q.create_trivia_result, dict(
                user_id = winner.id,
                topic = topic,
                answer = '',
                stamp = datetime.now(),
                server_id = server.id
            ))

    def get_points(self, user_id, server_id):
        with self.transaction() as trans:
            trans.execute(q.get_count, dict(
                user_id = user_id,
                server_id = server_id,
            ))

            return trans.fetchone()[0]

    def get_ranks(self, server_id, topic):
        query = q.get_ranks if topic is None else q.get_ranks_topic
        params = dict(server_id=server_id)
        if topic is not None:
            params['topic'] = topic

        with self.transaction() as trans:
            trans.execute(query, params)
            data = trans.fetchall()
            return data
