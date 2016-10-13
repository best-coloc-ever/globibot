from globibot.lib.helpers import parsing as p

from collections import namedtuple

DiceRoll = namedtuple('DiceRoll', ['count', 'face_count', 'modifier'])

dice_types = { 'd4', 'd6', 'd8', 'd10', 'd12', 'd20' }
dice_type_grammar = p.one_of(p.string, *dice_types)

def extract_dice_type(token):
    face_count_string = token.value[1:] # skipping the 'd' prefix

    return int(face_count_string)

dice_grammar = (
    p.maybe(p.integer) +
    (dice_type_grammar >> extract_dice_type)
).named('Dice')

dice_modifier_grammar = (
    (p.one_of(p.a, '+', '-') >> p.to_s) +
    p.integer
).named('Modifier')

def to_dice_roll(parsed):
    count, face_count, modifier = parsed

    # Default behavior when no prefix is specified is `1` dice
    if count is None:
        count = 1

    if modifier is None:
        modifier_value = 0
    else:
        sign, modifier_value = modifier
        if sign == '-':
            modifier_value = -modifier_value

    return DiceRoll(count, face_count, modifier_value)

dice_roll_parser = (
    dice_grammar +
    p.maybe(dice_modifier_grammar)
) >> to_dice_roll
