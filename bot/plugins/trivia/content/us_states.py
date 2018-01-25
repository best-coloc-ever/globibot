from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    _, data = item

    state_image_url = 'https:{}'.format(data['map_url'])
    state_image = await Utils.fetch(state_image_url)

    return dict(
        file_path=BytesIO(state_image),
        filename='state.png',
        content='You have {} seconds to guess the name of that state'.format(DELAY),
    )

def resolve(item, answers):
    state, data = item

    winner, message = Resolve.fastest(answers, state.lower(), skill='kkona')

    wiki_url = 'https://wikipedia.org{}'.format(data['path'])
    more_info = 'More information here: {}'.format(wiki_url)

    return winner, dict(
        content='{}\n{}'.format(message, more_info)
    )

USStatesTrivia = trivia_behavior(
    fetch   = Fetch.read_json('us_states.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
