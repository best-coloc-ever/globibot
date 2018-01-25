from .helpers import *
from .behavior import trivia_behavior

DELAY = 20

async def premise(item):
    trap, _ = item

    return dict(
        file_path='/tmp/globibot/{}'.format(trap),
        content='You have {} seconds to guess the gender of that character'.format(DELAY),
    )

def resolve(item, answers):
    _, gender = item

    winner, message = Resolve.fastest(answers, gender.lower(), skill='gender assuming')

    return winner, dict(content=message)

TrapsTrivia = trivia_behavior(
    fetch   = Fetch.read_json('traps.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
