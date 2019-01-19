from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f
from globibot.lib.helpers.hooks import master_only

from io import BytesIO
from shutil import rmtree
from collections import namedtuple

from .docker import AsyncDockerClient
from . import queries as q

import os

Environment = namedtuple(
    'Environment',
    ['id', 'author_id', 'name', 'language', 'image', 'dockerfile']
)

Snippet = namedtuple(
    'Snippet',
    ['id', 'author_id', 'name', 'language', 'code']
)

class Eval(Plugin):

    def load(self):
        self.docker = AsyncDockerClient()

        with self.transaction() as trans:
            trans.execute(q.fetch_behaviors)
            self.behaviors = [row[0] for row in trans.fetchall()]
            self.default_behavior = self.behaviors[0]

        self.last_snippets = dict()

    '''
    Commands
    '''

    eval_prefix = p.string('!eval')

    @command(p.bind(p.snippet, 'snippet'))
    async def eval_code(self, message, snippet):
        behavior = self.get_behavior(message.author.id)
        if behavior is None:
            await self.send_message(
                message.author,
                'Psst\nYou seem to have posted a `code snippet`\n'
                'I can evaluate it if you want\n'
                'Since your behavior was not defined, I set it to `manual`\n'
                'type `!eval help` for more information'
            )

        self.last_snippets[message.author.id] = snippet

        if behavior != 'auto':
            return

        await self.run_snippet(message, snippet, "")

    @command(eval_prefix + p.string('run'))
    async def eval_run(self, message):
        behavior = self.get_behavior(message.author.id)
        if behavior == 'off':
            return

        try:
            snippet = self.last_snippets[message.author.id]
            run_idx = message.content.index('run')
            await self.run_snippet(message, snippet, message.content[run_idx + len('run'):])
        except KeyError:
            pass

    @command(eval_prefix + p.string('save') + p.bind(p.word, 'name'))
    async def eval_save(self, message, name):
        try:
            snippet = self.last_snippets[message.author.id]
            snippets = self.get_snippets(message.author.id)
            try:
                next(s for s in snippets if s.name == name)
                await self.send_message(
                    message.channel,
                    '{} You already have a snippet named `{}`'
                        .format(message.author.mention, name),
                    delete_after = 30
                )
            except StopIteration:
                if self.save_snippet(message.author.id, name, snippet):
                    await self.send_message(
                        message.channel,
                        '{} your last snippet was saved as `{}`\n use `/{}` to run it'
                            .format(message.author.mention, name, name),
                        delete_after = 30
                    )
        except KeyError:
            pass

    @command(p.bind(p.word, 'name'))
    async def command_run(self, message, name):
        if not name.startswith('/'):
            return

        name = name[1:]
        snippet = self.get_snippet(message.author.id, name)
        if snippet:
            name_idx = message.content.index(name)
            args = message.content[name_idx + len(name):]
            await self.run_snippet(message, snippet, args)


    eval_env_prefix = eval_prefix + p.string('env')

    @command(eval_env_prefix + p.string('inspect') + p.bind(p.word, 'env_name'))
    async def eval_env_inspect(self, message, env_name):
        environments = self.get_environments(message.author.id)

        try:
            env = next(e for e in environments if e.name == env_name)
        except StopIteration:
            await self.send_message(
                message.channel,
                '{} You don\'t have any environment saved under the name `{}`'
                    .format(message.author.mention, env_name),
                delete_after=10
            )

        await self.send_message(
            message.channel,
            '{} `{}` environment was built from:\n{}'
                .format(
                    message.author.mention,
                    env_name,
                    f.code_block(env.dockerfile, language='dockerfile')
                )
        )

    @command(eval_env_prefix + p.string('list'))
    async def eval_env_list(self, message):
        environments = [
            env.name for env in self.get_environments(message.author.id)
            if env.author_id
        ]

        await self.send_message(
            message.channel,
            '{} You have `{}` saved environments\n{}'
                .format(
                    message.author.mention,
                    len(environments),
                    f.code_block(environments)
                )
        )

    @command(eval_env_prefix + p.string('map'))
    async def eval_env_map(self, message):
        environments = self.get_environments(message.author.id)

        padding = max(map(lambda env: len(env.language), environments), default=0)
        mapping = [
            '{:{}} ➡ {}'.format(env.language, padding, env.name)
            for env in environments
        ]

        await self.send_message(
            message.channel,
            '{} Here is your eval mapping\n{}'
                .format(
                    message.author.mention,
                    f.code_block(mapping)
                )
        )

    @command(eval_env_prefix + p.string('set')
                             + p.bind(p.word, 'language')
                             + p.bind(p.word, 'env_name'))
    async def eval_set(self, message, language, env_name):
        environments = self.get_environments(message.author.id)

        try:
            env = next(e for e in environments if e.name == env_name and e.author_id)
        except StopIteration:
            await self.send_message(
                message.channel,
                '{} You don\'t have any environment saved under the name `{}`'
                    .format(message.author.mention, env_name),
                delete_after=10
            )
            return

        # Removing old mappings
        for env in environments:
            if env.language == language:
                self.set_environment_language(env.id, 'none')
        # Flagging the env with the language
        self.set_environment_language(env.id, language)
        await self.send_message(
            message.channel,
            '{} Your `{}` snippets will now be evaluated with your `{}` environment'
                .format(message.author.mention, language, env_name)
        )

    @command(
        eval_env_prefix + p.string('library') + p.string('build')
                        + p.bind(p.word,    'env_name')
                        + p.bind(p.word,    'language')
                        + p.bind(p.snippet, 'snippet'),
        master_only
    )
    async def build_env_library(self, message, env_name, language, snippet):
        if snippet.language != 'dockerfile':
            return

        response_stream = await self.send_message(message.channel, 'Building...')
        dockerfile = BytesIO(snippet.code.encode('utf8'))
        flags = dict(errored=False)

        image = self.tag_name(env_name)
        build_stream = self.docker.async_build(
            fileobj=dockerfile,
            tag=image,
            decode=True,
            rm=True
        )

        def format_data(data):
            flags['errored'] = ('error' in data)
            return '\n'.join([str(v) for v in data.values()])

        errored = flags['errored']
        if not errored:
            self.save_environment(None, 'library/{}'.format(env_name), image, snippet.code, language)

        await self.stream_data(response_stream, build_stream, format_data)
        notice = 'Build errored' if errored else 'Build succeeded'
        await self.send_message(message.channel, notice)
        await self.delete_message_after(response_stream, 10)

    @command(
        eval_env_prefix + p.string('build')
                        + p.bind(p.word,    'env_name')
                        + p.bind(p.word,    'language')
                        + p.bind(p.snippet, 'snippet')
    )
    async def build_env(self, message, env_name, language, snippet):
        if snippet.language != 'dockerfile':
            return

        response_stream = await self.send_message(message.channel, 'Building...')
        dockerfile = BytesIO(snippet.code.encode('utf8'))
        flags = dict(errored=False)

        image = self.tag_name(env_name, message.author.id)
        build_stream = self.docker.async_build(
            fileobj=dockerfile,
            tag=image,
            decode=True,
            rm=True
        )

        def format_data(data):
            flags['errored'] = ('error' in data)
            return '\n'.join([str(v) for v in data.values()])

        errored = flags['errored']
        if not errored:
            self.save_environment(message.author.id, env_name, image, snippet.code, language)

        await self.stream_data(response_stream, build_stream, format_data)
        notice = 'Build errored' if errored else 'Build succeeded'
        await self.send_message(message.channel, notice)
        await self.delete_message_after(response_stream, 10)

    @command(
        p.string('!eval') + p.string('behavior')
                          + p.eof
    )
    async def user_behavior(self, message):
        behavior = self.get_behavior(message.author.id)
        if behavior is None:
            behavior = self.default_behavior

        await self.send_message(
            message.channel,
            '{} your eval behavior is `{}`'
                .format(message.author.mention, behavior),
            delete_after=5
        )

    @command(
        p.string('!eval') + p.string('behavior') + p.string('set')
                          + p.bind(p.word, 'behavior')
    )
    async def set_behavior(self, message, behavior):
        if behavior not in self.behaviors:
            return

        self.set_user_behavior(message.author.id, behavior)

        await self.send_message(
            message.channel,
            '{} your eval behavior has been set to `{}`'
                .format(message.author.mention, behavior),
            delete_after=5
        )

    '''
    details
    '''

    async def run_snippet(self, message, snippet, args):
        environment = self.get_environment(snippet.language, message.author.id)
        if environment is None:
            await self.send_message(
                message.channel,
                '{} You have no environment associated with the language `{}`'
                    .format(message.author.mention, snippet.language),
                delete_after=10
            )
        else:
            directory = '/tmp/globibot/{}'.format(message.author.id)
            os.makedirs(directory, exist_ok=True)
            with open('{}/{}'.format(directory, 'code.snippet'), 'w') as f:
                f.write(snippet.code)

            response_stream = await self.send_message(
                message.channel,
                '`Waiting for output`'
            )

            run_stream = self.docker.run_async(
                args,
                directory,
                environment.image,
                message.author.id
            )
            format_data = lambda line: line.decode('utf8')

            try:
                await self.stream_data(response_stream, run_stream, format_data)
                await self.send_message(message.channel, '`Exited`', delete_after=10)
            except AsyncDockerClient.Timeout:
                await self.send_message(message.channel, '`Evaluation timed out`')

            rmtree(directory)

    TAG_PREFIX = 'globibot_build'
    def tag_name(self, name, user_id=None):
        return '{}_{}:{}'.format(
            Eval.TAG_PREFIX,
            name,
            user_id if user_id else 'library'
        ),

    def get_behavior(self, user_id):
        with self.transaction() as trans:
            trans.execute(q.get_behavior, dict(
                author_id = user_id
            ))

            row = trans.fetchone()
            if row:
                return row[0]
            else:
                trans.execute(q.set_default_behavior, dict(
                    author_id = user_id,
                ))

    def set_user_behavior(self, user_id, behavior):
        with self.transaction() as trans:
            trans.execute(q.set_behavior, dict(
                author_id = user_id,
                behavior  = behavior
            ))

    def get_environment(self, language, user_id):
        with self.transaction() as trans:
            trans.execute(q.get_environment, dict(
                author_id = user_id,
                language  = language
            ))

            row = trans.fetchone()
            if row:
                return Environment(*row)

    def get_environments(self, user_id):
        with self.transaction() as trans:
            trans.execute(q.get_environments, dict(
                author_id = user_id,
            ))

            return [Environment(*row) for row in trans.fetchall()]

    def save_environment(self, user_id, env_name, image, dockerfile, language):
        with self.transaction() as trans:
            trans.execute(q.save_environment, dict(
                author_id  = user_id,
                name       = env_name,
                image      = image,
                dockerfile = dockerfile,
                language   = language
            ))

    def set_environment_language(self, env_id, language):
        with self.transaction() as trans:
            trans.execute(q.set_language, dict(
                id       = env_id,
                language = language
            ))

    def get_snippet(self, user_id, name):
        with self.transaction() as trans:
            trans.execute(q.get_snippet, dict(
                author_id = user_id,
                name      = name
            ))

            data = trans.fetchone()
            if data:
                return Snippet(*data)

    def get_snippets(self, user_id):
        with self.transaction() as trans:
            trans.execute(q.get_snippets, dict(
                author_id = user_id
            ))

            return [Snippet(*row) for row in trans.fetchall()]

    def save_snippet(self, user_id, name, snippet):
        with self.transaction() as trans:
            trans.execute(q.save_snippet, dict(
                author_id = user_id,
                name      = name,
                language  = snippet.language,
                code      = snippet.code
            ))

            return True
