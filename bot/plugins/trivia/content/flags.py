from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    country, image = item

    flag_image_url = 'https://www.countries-ofthe-world.com/{}'.format(image)
    flag_image = await Utils.fetch(flag_image_url)

    return dict(
        file_path=BytesIO(flag_image),
        filename='flag.png',
        content='You have {} seconds to guess the name of that country'.format(DELAY),
    )

def resolve(item, answers):
    country, _ = item

    winner, message = Resolve.fastest(answers, country.lower(), skill='geography')

    return winner, dict(content=message)

FlagsTrivia = trivia_behavior(
    fetch   = Fetch.read_json('flags.json'),
    pick    = Pick.random_collection,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
