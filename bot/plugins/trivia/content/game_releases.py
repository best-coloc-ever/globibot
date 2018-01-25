from .helpers import *
from .behavior import trivia_behavior

DELAY = 20

async def premise(item):
    name, data = item

    return dict(
        content='You have {} seconds to guess the year of release of `{}`\n{}'
            .format(DELAY, name, 'https:{}'.format(data['image_url'])),
    )

def resolve(item, answers):
    _, data = item

    winner, message = Resolve.closest_int(
        answers,
        data['year'],
        within=5,
        skill='nerd'
    )

    wiki_url = 'https://wikipedia.org{}'.format(data['path'])
    more_info = 'More information here: {}'.format(wiki_url)

    return winner, dict(
        content='{}\n{}'.format(message, more_info)
    )

GameReleasesTrivia = trivia_behavior(
    fetch   = Fetch.read_json('games.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
