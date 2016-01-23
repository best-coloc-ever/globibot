import twitchcast
import twitch

def list_commands():
    def pretty_command(cmd):
        desc, pattern, _ = cmd
        return '**`{}`**\n        *{}*'.format(pattern[1:], desc)

    header = '**Globibot-twitch commands:**'

    return '{}\n{}'.format(
        header,
        '\n'.join(map(pretty_command, COMMANDS))
    )

TWITCHCAST_COMMANDS = [
    (
        'List streams',
        '^!streams',
        twitchcast.streams
    ),
    (
        'Query a stream',
        '^!stream (?P<stream_id>\d+)',
        twitchcast.stream
    ),
    (
        'Monitor a stream',
        '^!monitor (?P<channel>\w+) (?P<quality>best|high|medium|low|worst)',
        twitchcast.monitor
    ),
    (
        'Unmonitor a stream',
        '^!unmonitor (?P<stream_id>\d+)',
        twitchcast.unmonitor
    ),
    (
        'Watch a stream',
        '^!watch (?P<stream_id>\d+)',
        twitchcast.watch
    ),
    (
        'Unwatch a stream',
        '^!unwatch (?P<stream_id>\d+)',
        twitchcast.unwatch
    ),
]

TWITCH_COMMANDS = [
    (
        'List top channels on Twitch',
        '^!channels\s?(?P<limit>\d+)?',
        twitch.top_channels
    ),
    (
        'List top games on Twitch',
        '^!games\s?(?P<limit>\d+)?',
        twitch.top_games
    ),
]

GENERIC_COMMANDS = [
    (
        'List commands',
        '^!commands',
        list_commands
    )
]

COMMANDS = TWITCHCAST_COMMANDS + TWITCH_COMMANDS + GENERIC_COMMANDS
