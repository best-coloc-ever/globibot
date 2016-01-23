import requests
import json

def top_channels(limit):
    if limit is None:
        limit = 5

    if int(limit) > 100:
        return 'Cannot fetch more than 100 channels'

    def to_response(stream):
        return {
            'channel': stream['channel']['name'],
            'game': stream['game'],
            'viewers': stream['viewers']
        }

    response = requests.get(
        'https://api.twitch.tv/kraken/streams',
        params={
            'limit': limit
        }
    )
    if response.ok:
        streams = response.json()['streams']
        channels = list(map(to_response, streams))
        return '```json\n{}\n```'.format(json.dumps(channels, indent=4))

def top_games(limit):
    if limit is None:
        limit = 5

    if int(limit) > 100:
        return 'Cannot fetch more than 100 channels'

    def to_response(game):
        return {
            'name': game['game']['name'],
            'channels': game['channels'],
            'viewers': game['viewers'],
        }

    response = requests.get(
        'https://api.twitch.tv/kraken/games/top',
        params={
            'limit': limit
        }
    )
    if response.ok:
        games = response.json()['top']
        games = list(map(to_response, games))
        return '```json\n{}\n```'.format(json.dumps(games, indent=4))
