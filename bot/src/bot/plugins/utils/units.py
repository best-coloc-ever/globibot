from funcparserlib import parser as fp
from bot.lib.helpers import parsing as p

from collections import namedtuple

UnitValue = namedtuple('UnitValue', ['value', 'unit'])

ratio = lambda ratio: lambda x: x * ratio
f_to_c = lambda x: (x - 32) / 1.8

UNITS = {
    'inch':       (ratio(2.54), 'cm'),
    'inches':     (ratio(2.54), 'cm'),
    'foot':       (ratio(30.48), 'cm'),
    'feet':       (ratio(30.48), 'cm'),
    'mile':       (ratio(1.60934), 'km'),
    'miles':      (ratio(1.60934), 'km'),
    'pound':      (ratio(0.453592), 'kg'),
    'pounds':     (ratio(0.453592), 'kg'),
    '°f':         (f_to_c, '°C'),
    'fahrenheit': (f_to_c, '°C'),
}

to_s_lowered = lambda tok: tok.value.lower()
unit_parser = p.some(lambda tok: to_s_lowered(tok) in UNITS) >> to_s_lowered

@fp.Parser
def unit_value_parser(tokens, s):
    if s.pos >= len(tokens) - 1:
        raise fp.NoParseError(u'no tokens left in the stream', s)
    else:
        value, s1 = p.number.run(tokens, s)
        unit, s2 = unit_parser.run(tokens, s1)

        return UnitValue(value, unit), s2

unit_value_parser.name = 'U'
