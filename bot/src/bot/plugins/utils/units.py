from funcparserlib import parser as fp
from bot.lib.helpers import parsing as p

class Value:

    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __add__(self, other):
        assert(type(self.unit) is type(other.unit))

        n1 = increase_max(self)
        n2 = increase_max(other)

        if n1.unit != n2.unit:
            n2 = increase_max(system_convert(n2))

        assert(n1.unit == n2.unit)

        return normalize(Value(n1.unit, n1.value + n2.value))

    def __str__(self):
        output = '{:.2f} {}'.format(self.value, self.unit.name)

        normalized = normalize(self)
        if normalized.unit != self.unit:
            output += ' ({})'.format(normalized)

        return output

class Unit:

    def __init__(self, name, *abrevs):
        self.name = name
        self.names = tuple(n.lower() for n in (name,) + abrevs)

    def __call__(self, value):
        return Value(self, value)

class Distance(Unit): pass

inch = Distance('in', 'inch', 'inches', "''", '"')
foot = Distance('ft', 'foot', 'feet',   "'")
yard = Distance('yd', 'yard', 'yards')
mile = Distance('mi', 'mile', 'miles')

mm   = Distance('mm', 'millimeter', 'millimeters')
cm   = Distance('cm', 'centimeter', 'centimeters')
m    = Distance('m',  'meter',      'meters')
km   = Distance('km', 'kilometer',  'kilometers')

class Temperature(Unit): pass

fahrenheit = Temperature('°F', 'fahrenheit', 'fahrenheits', 'f')
centigrad  = Temperature('°C', 'centigrad',  'centigrads',  'c')

UNITS = [
    # Distances
    inch, foot, yard, mile,
    mm, cm, m, km,
    # Temperatures
    fahrenheit,
    centigrad
]

UNITS_BY_NAME = dict(
    (name, unit) for unit in UNITS
                 for name in unit.names
)

class Conversion:

    def __init__(self, u_from, u_to, converter):
        assert(type(u_from) is type(u_to))

        self.u_from = u_from
        self.u_to = u_to
        self.converter = converter

    def __call__(self, val):
        assert(val.unit == self.u_from)

        return Value(self.u_to, self.converter(val.value))

def simple_ratio(v1, v2):
    return Conversion(
        v1.unit,
        v2.unit,
        lambda v: v * (v2.value / v1.value)
    )

def two_way_ratio(v1, v2):
    return (
        simple_ratio(v1, v2),
        simple_ratio(v2, v1)
    )

SYSTEM_CONVERSIONS = [
    *two_way_ratio(inch(1), mm(25.4)),
    *two_way_ratio(foot(1), cm(30.48)),
    *two_way_ratio(yard(1), m(0.9144)),
    *two_way_ratio(mile(1), km(1.60934)),

    Conversion(fahrenheit, centigrad, lambda f: (f - 32) / 1.8),
    Conversion(centigrad, fahrenheit, lambda c: c * 1.8 + 32),
]

SYSTEM_CONVERSIONS_BY_UNIT = dict(
    (conversion.u_from, conversion)
    for conversion in SYSTEM_CONVERSIONS
)

REDUCE_CONVERSIONS = [
    simple_ratio(mm(10), cm(1)),
    simple_ratio(cm(100), m(1)),
    simple_ratio(m(1000), km(1)),

    simple_ratio(inch(12), foot(1)),
    simple_ratio(foot(3), yard(1)),
    simple_ratio(yard(1760), mile(1)),
]

REDUCE_CONVERSIONS_BY_UNIT = dict(
    (conversion.u_from, conversion)
    for conversion in REDUCE_CONVERSIONS
)

INCREASE_CONVERSIONS = [
    simple_ratio(cm(1), mm(10)),
    simple_ratio(m(1), cm(100)),
    simple_ratio(km(1), m(1000)),

    simple_ratio(foot(1), inch(12)),
    simple_ratio(yard(1), foot(3)),
    simple_ratio(mile(1), yard(1760)),
]

INCREASE_CONVERSIONS_BY_UNIT = dict(
    (conversion.u_from, conversion)
    for conversion in INCREASE_CONVERSIONS
)

def system_convert(value):
    try:
        conversion = SYSTEM_CONVERSIONS_BY_UNIT[value.unit]
    except KeyError:
        return value

    return conversion(value)

def reduce_convert(value):
    try:
        conversion = REDUCE_CONVERSIONS_BY_UNIT[value.unit]
    except KeyError:
        return value

    converted = conversion(value)
    if converted.value >= 1:
        return reduce_convert(converted)
    return value

def increase_convert(value):
    try:
        conversion = INCREASE_CONVERSIONS_BY_UNIT[value.unit]
    except KeyError:
        return value

    converted = conversion(value)
    if converted.value < 1:
        return increase_convert(converted)
    return value

def increase_max(value):
    try:
        conversion = INCREASE_CONVERSIONS_BY_UNIT[value.unit]
        return increase_max(conversion(value))
    except KeyError:
        return value

def normalize(value):
    if value.value >= 1:
        return reduce_convert(value)
    else:
        return increase_convert(value)

def sum_units(unit, *units):
    acc = unit
    for u in units:
        acc += u
    return acc

to_s_lowered = lambda tok: tok.value.lower()
unit_parser = p.some(
    lambda tok: to_s_lowered(tok) in UNITS_BY_NAME
) >> to_s_lowered

@fp.Parser
def unit_value_parser(tokens, s):
    if s.pos >= len(tokens) - 1:
        raise fp.NoParseError(u'no tokens left in the stream', s)
    else:
        value, s1 = p.number.run(tokens, s)
        unit_name, s2 = unit_parser.run(tokens, s1)

        return Value(UNITS_BY_NAME[unit_name], value), s2

unit_value_parser.name = 'U'
