from globibot.lib.web.handlers import SessionHandler
from globibot.lib.web.decorators import authenticated, respond_json, with_body_arguments, respond_json_async

from discord import ChannelType

from .player import ItemType

WHITELISTED_DJ_ADMINS = [
    '89108411861467136', # Globi
    '98469036936945664', # Marcus
    '124948152414502914', # Fanta
    '123149655126048769', # Fanta's bf
    '120264712880521218', # ErPacheco
]

def server_data(server):
    return dict(
        id       = server.id,
        name     = server.name,
        icon_url = server.icon_url
    )

def voice_data(server, user):
    def valid_voice(chan):
        member = server.get_member(user.id)
        if chan.type != ChannelType.voice:
            return False
        return chan.permissions_for(member).connect

    return [
        dict(
            id   = channel.id,
            name = channel.name,
        )
        for channel in filter(valid_voice, server.channels)
    ]

@with_body_arguments('server_id', 'channel_id')
async def join_voice(handler, server_id, channel_id):
    if handler.current_user.id not in WHITELISTED_DJ_ADMINS:
        return dict(error='You are not allowed to do that')

    server = handler.bot.find_server(server_id)

    if server is None:
        return dict(error='Unknown server')

    channel = server.get_channel(channel_id)

    if channel is None:
        return dict(error='Unknown channel')

    await handler.plugin.join_voice(channel)

    return dict(message='Ok')

@with_body_arguments('server_id')
async def leave_voice(handler, server_id):
    if handler.current_user.id not in WHITELISTED_DJ_ADMINS:
        return dict(error='You are not allowed to do that')

    server = handler.bot.find_server(server_id)

    if server is None:
        return dict(error='Unknown server')

    await handler.plugin.leave_voice(server)

    return dict(message='Ok')

@with_body_arguments('server_id', 'content')
async def tts(handler, server_id, content):
    server = handler.bot.find_server(server_id)

    if server is None:
        return dict(error='Unknown server')

    await handler.plugin.queue_tts(server, handler.current_user, content)

    return dict(message='Ok')

@with_body_arguments('server_id', 'lang')
async def tts_lang(handler, server_id, lang):
    server = handler.bot.find_server(server_id)

    if server is None:
        return dict(error='Unknown server')

    if await handler.plugin.tts.set_server_language(server, lang):
        return dict(message='Ok')
    else:
        return dict(error='Invalid language')

@with_body_arguments('server_id', 'song')
async def queue_song(handler, server_id, song):
    server = handler.bot.find_server(server_id)

    if server is None:
        return dict(error='Unknown server')

    if await handler.plugin.queue_item(server, handler.current_user, ItemType.YTDLLink, song):
        return dict(message='Ok')
    else:
        return dict(error='Invalid language')

ACTIONS = dict((
    ('join', join_voice),
    ('leave', leave_voice),
    ('tts', tts),
    ('tts-lang', tts_lang),
    ('queue', queue_song)
))

class VoiceHandler(SessionHandler):

    @authenticated
    @respond_json_async
    @with_body_arguments('action_type')
    async def post(self, action_type):
        try:
            action = ACTIONS[action_type]
        except KeyError:
            return dict(error='Unknown action')
        else:
            response = await action(self)
            return response

    @authenticated
    @respond_json
    def get(self):
        return [
            dict(
                server = server_data(server),
                channels = voice_data(server, self.bot.user)
            )
            for server in self.bot.servers_of(self.current_user)
        ]
