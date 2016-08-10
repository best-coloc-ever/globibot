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

class Length(Unit): pass

inch = Length('in', 'inch', 'inches', "''", '"')
foot = Length('ft', 'foot', 'feet',   "'")
yard = Length('yd', 'yard', 'yards')
mile = Length('mi', 'mile', 'miles')

mm   = Length('mm', 'millimeter', 'millimeters')
cm   = Length('cm', 'centimeter', 'centimeters')
m    = Length('m',  'meter',      'meters')
km   = Length('km', 'kilometer',  'kilometers')

class Mass(Unit): pass

oz = Mass('oz', 'ounce', 'ounces')
lb = Mass('lb', 'pound', 'pounds')

mg = Mass('mg', 'milligram', 'milligrams')
g  = Mass('g',  'gram',      'grams')
kg = Mass('kg', 'kilogram',  'kilograms')

class Volume(Unit): pass

pt     = Volume('pt', 'pint', 'pints')
gallon = Volume('gallon', 'gallons')

ml     = Volume('mL', 'milliliter', 'milliliters')
l      = Volume('L', 'liter', 'liters')

class Temperature(Unit): pass

fahrenheit = Temperature('°F', 'fahrenheit', 'fahrenheits', 'f')

centigrad  = Temperature('°C', 'centigrad',  'centigrads',  'c')
kelvin     = Temperature('°K',  'kelvin', 'kelvins', 'k')


UNITS = [
    # Lengths
    inch, foot, yard, mile,
    mm, cm, m, km,
    # Masses
    oz, lb,
    mg, g, kg,
    # Volumes,
    pt, gallon,
    ml, l,
    # Temperatures
    fahrenheit,
    centigrad, kelvin
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

    *two_way_ratio(oz(1), mg(28349.5)),
    *two_way_ratio(oz(1), g(28.3495)),
    *two_way_ratio(lb(1), kg(0.453592)),

    *two_way_ratio(pt(1), ml(473.176)),
    *two_way_ratio(gallon(1), l(3.78541)),

    Conversion(fahrenheit, centigrad, lambda f: (f - 32) / 1.8),
    Conversion(centigrad, fahrenheit, lambda c: c * 1.8 + 32),
    Conversion(kelvin, fahrenheit, lambda k: k * 1.8 - 459.67)
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

    simple_ratio(oz(16), lb(1)),

    simple_ratio(mg(1000), g(1)),
    simple_ratio(g(1000), kg(1)),

    simple_ratio(pt(8), gallon(1)),

    simple_ratio(ml(1000), l(1)),
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

    simple_ratio(lb(1), oz(16)),

    simple_ratio(g(1), mg(1000)),
    simple_ratio(kg(1), g(1000)),

    simple_ratio(gallon(1), pt(8)),

    simple_ratio(l(1), ml(1000)),
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
