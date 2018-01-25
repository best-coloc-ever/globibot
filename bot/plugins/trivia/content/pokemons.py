from .helpers import *
from .behavior import trivia_behavior

from io import BytesIO

DELAY = 20

async def premise(item):
    _, pokemon_image_url = item

    pokemon_image = await Utils.fetch(pokemon_image_url)

    return dict(
        file_path=BytesIO(pokemon_image),
        filename='pokemon.png',
        content='You have {} seconds to guess the name of that pokemon'.format(DELAY),
    )

def resolve(item, answers):
    country, _ = item

    winner, message = Resolve.fastest(answers, country.lower(), skill='weeb')

    return winner, dict(content=message)

PokemonsTrivia = trivia_behavior(
    fetch   = Fetch.read_json('pokemons.json'),
    pick    = Pick.random_collection,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
