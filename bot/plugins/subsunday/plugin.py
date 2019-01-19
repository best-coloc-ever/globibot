from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f

from globibot.lib.web.handlers import ContextHandler
from globibot.lib.web.decorators import respond_json

import json
import csv
import websockets
import base64
import asyncio
from collections import namedtuple

from io import StringIO
from http import HTTPStatus

from tornado.escape import json_encode

from datetime import datetime

from utils.logging import logger

Format = namedtuple('Format', ['mime_type', 'encoder'])

def require_basic_auth(handler_class):
    def wrap_execute(handler_execute):
        def require_basic_auth(handler, kwargs):
            auth_header = handler.request.headers.get('Authorization')
            if auth_header is None or not auth_header.startswith('Basic '):
                handler.set_status(401)
                handler.set_header('WWW-Authenticate', 'Basic realm=Restricted')
                handler._transforms = []
                handler.finish()
                return False
            auth_decoded = base64.decodestring(auth_header[6:].encode())
            logger.debug(auth_decoded)
            kwargs['user'], kwargs['password'] = auth_decoded.split(b':', 2)
            return True
        def _execute(self, transforms, *args, **kwargs):
            if not require_basic_auth(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)
        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class

def csv_encode(data):
    encoded = StringIO()

    writer = csv.DictWriter(encoded, ['USERNAME', 'CHOICE', 'FROMCHAT'])
    writer.writeheader()
    writer.writerows(
        {'USERNAME': user, 'CHOICE': game, 'FROMCHAT': True }
        for user, game in data.items()
    )

    return encoded.getvalue()

@require_basic_auth
class SubsubdayVotesHandler(ContextHandler):

    FORMATS = {
        'json': Format('application/json', json_encode),
        'csv': Format('text/plain', csv_encode)
    }

    def get(self, user, password):
        data = self.plugin.votes

        if user != 'gav' or password != ')rhvp}NMm6a/':
            self.set_status(HTTPStatus.BAD_REQUEST)
            return

        try:
            response_format = self.get_query_argument('format')
        except:
            response_format = 'json'

        try:
            download = self.get_query_argument('download')
            filename = 'lirik_votes_{}'.format(datetime.utcnow().isoformat())
            extension = response_format
            self.set_header('Content-Disposition', 'attachment; filename={}.{};'.format(filename, extension))
        except:
            pass

        try:
            format_ = SubsubdayVotesHandler.FORMATS[response_format]
        except KeyError:
            self.set_status(HTTPStatus.BAD_REQUEST)
        else:
            self.set_header('Content-Type', format_.mime_type)
            self.write(format_.encoder(data))

class Subsunday(Plugin):

    VOTES_FILE = '/tmp/globibot/votes.json'
    VOTE_PREFIX = '!vote '
    WS_ENDPOINT = 'wss://datcoloc.com/chat/lirik'

    def load(self):
        self.add_web_handlers(
            (r'/subsunday/votes', SubsubdayVotesHandler, dict(plugin=self)),
        )

        self.votes = self.load_votes()
        self.debug('Loaded {} votes'.format(len(self.votes)))

        self.run_async(self.read_votes_forever())

    def load_votes(self):
        try:
            with open(Subsunday.VOTES_FILE, 'r') as f:
                return json.load(f)
        except:
            return dict()

    def dump_votes(self):
        with open(Subsunday.VOTES_FILE, 'w') as f:
            json.dump(self.votes, f)

    async def read_votes_forever(self):
        while True:
            self.debug('Connecting to chat...')

            async with websockets.connect(Subsunday.WS_ENDPOINT) as ws:
                self.debug('Connected to chat')
                while True:
                    try:
                        data = await ws.recv()
                        message = json.loads(data)
                    except:
                        break
                    else:
                        self.process_chat_message(message)

            self.warning('Disconnected from chat')
            await asyncio.sleep(10)

    def process_chat_message(self, message):
        try:
            is_subscriber = (message['tags']['subscriber'] == '1')
        except KeyError:
            return
        else:
            if not is_subscriber:
                return

        user = message['sender']
        content = message['content'].strip().lower()
        if content.startswith(Subsunday.VOTE_PREFIX):
            game_name = content[len(Subsunday.VOTE_PREFIX):].strip()

            self.debug('"{}" voted for "{}"'.format(user, game_name))

            self.votes[user] = game_name
            self.dump_votes()

    @command(p.string('!votes'))
    async def votes(self, message):
        await self.send_message(
            message.channel,
            '{} votes registered so far: https://globibot.com/bot/subsunday/votes'
                .format(len(self.votes))
        )
