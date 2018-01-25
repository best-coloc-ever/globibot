from .helpers import *
from .behavior import trivia_behavior

DELAY = 20

import random

async def premise(item):
    _, data = item

    snippet = random.choice(data['snippets'])
    code = snippet['code']

    if '```' in code:
        warning = '\n⚠️The code contained triple backquotes that were replaced by triple quotes'
        code.replace('```', '\'\'\'')
    else:
        warning = ''

    return dict(
        content='You have {} seconds to guess the name of the language used '
                'in the following snippet about `{}`:{}\n```\n{}```'
                    .format(DELAY, snippet['name'], warning, snippet['code']),
    )

def resolve(item, answers):
    name, data = item

    winner, message = Resolve.fastest(answers, name.lower(), skill='"programming"')

    url = 'http://rosettacode.org{}'.format(data['path'])
    more_info = 'More information here: <{}>'.format(url)

    return winner, dict(
        content='{}\n{}'.format(message, more_info)
    )

ProgrammingTrivia = trivia_behavior(
    fetch   = Fetch.read_json('programming.json'),
    pick    = Pick.random_dict_item,
    premise = premise,
    query   = Query.timed(DELAY),
    resolve = resolve,
)
