from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    animal, data = item

    animal_image_url = 'https:{}'.format(data['image'])
    animal_image = await Utils.fetch(animal_image_url)

    return dict(
        file_path=BytesIO(animal_image),
        filename='animal.png',
        content='You have {} seconds to guess the name of that animal'.format(DELAY),
    )

def resolve(item, answers):
    animal, data = item

    winner, message = Resolve.fastest(answers, animal.lower(), skill='fauna')

    wiki_url = 'https://wikipedia.org{}'.format(data['path'])
    more_info = 'More information here: {}'.format(wiki_url)

    return winner, dict(
        content='{}\n{}'.format(message, more_info)
    )

AnimalsTrivia = trivia_behavior(
    fetch   = Fetch.read_json('animals.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
