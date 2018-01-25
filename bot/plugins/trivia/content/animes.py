from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    anime, data = item

    anime_image = await Utils.fetch(data['image'])

    return dict(
        file_path=BytesIO(anime_image),
        filename='anime.png',
        content='You have {} seconds to guess the title of that anime'.format(DELAY),
    )

def resolve(item, answers):
    anime, data = item

    winner, message = Resolve.fastest(answers, anime.lower(), skill='weeb')

    more_info = 'More information here: {}'.format(data['path'])

    return winner, dict(
        content='{}\n{}'.format(message, more_info)
    )

AnimesTrivia = trivia_behavior(
    fetch   = Fetch.read_json('animes.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
