from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    _, token = item

    flag_image_url = f'https://glo.bi/trivia/flags/{token}.png'

    return dict(
        content=f'You have {DELAY} seconds to guess the name of that country\n{flag_image_url}'
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
