from .helpers import *
from .behavior import trivia_behavior

DELAY = 20

async def premise(item):
    country, _ = item

    return dict(
        content='You have {} seconds to guess the name of the capital city of `{}`'
                    .format(DELAY, country),
    )

def resolve(item, answers):
    _, capital = item

    winner, message = Resolve.fastest(answers, capital.lower(), skill='geography')

    return winner, dict(content=message)

CapitalsTrivia = trivia_behavior(
    fetch   = Fetch.read_json('capitals.json'),
    pick    = Pick.random_collection,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
