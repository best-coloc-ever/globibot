from bot.lib.module import Module
from bot.lib.decorators import simple_command, command
from bot.lib.helpers import parsing as p

from . import constants as c

from collections import defaultdict
from time import time

import asyncio
import docker

class Eval(Module):

    class Timeout(Exception):
        pass

    class Behavior:
        Auto = 'auto'
        Ask = 'ask'
        Off = 'off'

    BEHAVIORS = [
        Behavior.Auto,
        Behavior.Ask,
        Behavior.Off,
    ]

    WORK_DIR = '/app'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_behaviors = defaultdict(lambda: Eval.Behavior.Ask)
        self.behaviors = {
            Eval.Behavior.Auto: self.eval_code,
            Eval.Behavior.Ask: self.ask_for_eval,
            Eval.Behavior.Off: self.ignore,
        }
        self.user_snippets = defaultdict(dict)
        self.user_last_snippets = dict()

        self.language_map = {
            'rust': lambda code: self.file_eval_container(code, 'rs', 'schickling/rust', 'rustc {file} && ./main'),
            'python': lambda code: self.simple_eval_container('python:3.5', ('python3', '-c', code)),
            'ruby': lambda code: self.simple_eval_container('ruby:2.3', ('ruby', '-e', code)),
            'c': lambda code: self.file_eval_container(code, 'c', 'gcc:5.3', 'gcc {file} && ./a.out'),
            'cpp': lambda code: self.file_eval_container(code, 'cpp', 'gcc:5.3', 'g++ -std=c++1z {file} && ./a.out'),
            'haskell': lambda code: self.file_eval_container(code, 'hs', 'haskell:7.10', 'ghc {file} && ./main'),
            'javascript': lambda code: self.file_eval_container(code, 'js', 'remnux/v8', 'd8 {file}'),
            'php': lambda code: self.file_eval_container(code, 'php', 'php:7.0', 'php {file}'),
            'java': lambda code: self.file_eval_container(code, 'java', 'java:9', 'javac {file} && java main'),
            'go': lambda code: self.file_eval_container(code, 'go', 'golang:1.6', 'go build && ./app'),
            'brainfuck': lambda code: self.file_eval_container(code, 'b', 'globidocker/brainfuck', 'bfc {file} && ./a.out'),
        }

        self.client = docker.Client()
        self.timeout = c.DEFAULT_TIMEOUT

    def simple_eval_container(self, image, command):
        container = self.client.create_container(
            image=image,
            command=command,
            user='root',
            working_dir=Eval.WORK_DIR,
        )
        self.client.update_container(
            container,
            cpuset_cpus=c.CPU_SET
        )

        return container

    def file_eval_container(self, code, extension, image, command):
        file_name = '{}/main.{}'.format(Eval.WORK_DIR, extension)
        shell_escape = lambda string: '"{}"'.format(string.replace('"', '\\"'))
        shell_command = ' '.join([
            'echo', shell_escape(code), '>', file_name, '&&',
            command.format(file=file_name)
        ])

        return self.simple_eval_container(image, ('bash', '-c', shell_command))

    @simple_command('```{language:w}\n{code}\n```')
    async def on_code_block(self, message, language, code):
        language = language.lower()
        # Ensure language is supported
        if language not in self.language_map:
            return
        # Save snippet for user
        self.user_last_snippets[message.author.id] = (language, code)
        # Act according to its eval behavior
        user_behavior = self.user_behaviors[message.author.id]
        action = self.behaviors[user_behavior]
        await action(message, language, code)

    async def eval_code(self, message, language, code):
        computing_message = await self.send_message(
            message.channel,
            'Computing...',
        )

        container_builder = self.language_map[language]
        container = container_builder(code)

        await self.eval_container(message.channel, container)
        await self.bot.delete_message(computing_message)

    async def ask_for_eval(self, message, language, code):
        await self.send_message(
            message.channel,
            '{} I saved your `{}` snippet, you can evaluate it with `!eval`'
                .format(message.author.mention, language)
        )

    async def ignore(self, *args):
        pass

    @command(p.string('!eval') + p.eof)
    async def eval_last_request(self, message):
        try:
            language, code = self.user_last_snippets[message.author.id]
            await self.eval_code(message, language, code)
        except KeyError:
            await self.send_message(
                message.channel,
                '{}: You have no registered snippets'
                    .format(message.author.mention)
            )

    @command(p.string('!eval') + p.bind(p.word, 'name') + p.eof)
    async def eval_request(self, message, name):
        try:
            language, code = self.user_snippets[message.author.id][name]
            await self.eval_code(message, language, code)
        except KeyError:
            await self.send_message(
                message.channel,
                '{}: You have no registered snippets named `{}`'
                    .format(message.author.mention, name)
            )

    behavior = p.one_of(p.string, *BEHAVIORS) >> p.to_s
    @command(p.string('!eval') + p.string('behavior') + p.bind(behavior, 'behavior'))
    async def change_eval_behavior(self, message, behavior):
        self.user_behaviors[message.author.id] = behavior
        await self.send_message(
            message.channel,
            '{} your eval behavior is now set to `{}`'
                .format(message.author.mention, behavior)
        )

    @command(p.string('!eval') + p.string('languages'))
    async def list_languages(self, message):
        await self.send_message(
            message.channel,
            'I support the following languages:\n'
            '```\n'
            '{}\n'
            '```'
                .format('\n'.join(sorted(self.language_map.keys())))
        )

    @command(p.string('!eval') + p.string('save') + p.bind(p.word, 'name'))
    async def save_snippet(self, message, name):
        user_id = message.author.id
        try:
            snippet = self.user_last_snippets[user_id]
            self.user_snippets[user_id][name] = snippet
            await self.send_message(
                message.channel,
                '{} Your last snippet is now registered under the name `{}`\n'
                'You an invoke it with `!eval {}`'
                    .format(message.author.mention, name, name)
            )
        except KeyError:
            await self.send_message(
                message.channel,
                '{} I don\'t have any snippets from you'
                    .format(message.author.mention)
            )

    async def wait_for_container(self, container):
        started = time()

        while True:
            await asyncio.sleep(0.5)
            state = self.client.inspect_container(container)
            if not state['State']['Running']:
                break
            if time() - started > self.timeout:
                raise Eval.Timeout

    async def eval_container(self, channel, container):
        self.debug('starting eval container: {}'.format(container))
        self.client.start(container)

        try:
            await self.wait_for_container(container)
        except Eval.Timeout:
            await self.bot.send_message(
                channel,
                'Evaluation timed out after {} seconds'.format(self.timeout)
            )
        finally:
            logs = self.client.logs(container, stream=True)
            self.client.remove_container(container, force=True, v=True)
            lines = []
            elided = False
            for i, line in enumerate(logs):
                if i >= c.MAX_OUTPUT_LINES:
                    elided = True
                    break
                lines.append(line.decode('utf-8'))
            if lines:
                await self.bot.send_message(
                    channel,
                    '{}{}'.format(
                        ''.join(lines),
                        '`lines omitted...`' if elided else ''
                    )
                )
            else:
                await self.bot.send_message(
                    channel,
                    '`No output`'
                )

