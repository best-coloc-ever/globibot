from collections import namedtuple

Giveaway = namedtuple('Giveaway', [
    'user',
    'server',
    'title',
    'content',
    'timeout'
])
