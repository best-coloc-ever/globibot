from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command

from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f

from .grammar import DiceRoll, dice_roll_parser
from . import invariants as inv

from random import randint
from itertools import groupby

# Takes dice [adN + x, bdN + y, cdN + z] and
# returns a reduced die (a+b+c)dN + (x+y+z)
reduce_dice_group = lambda dice: DiceRoll(
    count      = sum(map(DiceRoll.count.__get__, dice)),
    face_count = dice[0].face_count,
    modifier   = sum(map(DiceRoll.modifier.__get__, dice))
)

def group_dice(dice):
    byFaceCount = DiceRoll.face_count.__get__
    sorted_dices = sorted(dice, key=byFaceCount)

    return [
        reduce_dice_group(list(dice_group))
        for _, dice_group in groupby(sorted_dices, byFaceCount)
    ]

def enforce_dnd_invariants(dice):
    # Check dice count
    total_dice = sum(map(DiceRoll.count.__get__, dice))

    if total_dice > inv.MAX_DICE_COUNT:
        raise inv.TooManyDicesError(total_dice)

    # Check the d20 limit
    try:
        d20s = next(die for die in dice if die.face_count == 20)
    except StopIteration:
        pass # No d20s, we are good
    else:
        if d20s.count > inv.MAX_D20_COUNT:
            raise inv.TooManyD20sError(d20s.count)

    # Check the modifiers bound
    for die in dice:
        if not inv.MODIFIER_MIN_BOUND <= die.modifier <= inv.MODIFIER_MAX_BOUND:
            raise inv.ModifierOutOfBounds(die.modifier)

def roll_die(die):
    # The magic happens at the line below
    results = [randint(1, die.face_count) for _ in range(die.count)]
    total = max(sum(results) + die.modifier, 0)

    modifier_sign = '+' if die.modifier > 0 else '-'

    description = '{} d{}'.format(die.count, die.face_count)
    if die.modifier != 0:
        description += ' {} {}'.format(modifier_sign, abs(die.modifier))

    result_string = ' + '.join(map(str, results))
    if die.modifier != 0:
        result_string += ' {} (mod){}'.format(modifier_sign, abs(die.modifier))

    if die.modifier != 0 or die.count > 1:
        result_string += ' = {}'.format(total)

    # Special display of critical fails and hits for d20s
    if die.face_count == 20:
        if results[-1] <= 1:
            result_string += ' (Critical Fail!)'
        elif results[-1] >= 20:
            result_string += ' (Critical Hit!)'

    return '{:10} => {}'.format(description, result_string)

class Dnd(Plugin):

    @command(
        p.string('!roll') +
        p.bind(p.oneplus(dice_roll_parser), 'dice') +
        p.eof
    )
    async def roll_dice_command(self, message, dice):
        grouped_dice = group_dice(dice)
        enforce_dnd_invariants(grouped_dice)

        results = map(roll_die, grouped_dice)

        response = (
            '{} 🎲 rolling your dice\n'
            '{}'
                .format(
                    message.author.mention,
                    f.code_block('\n'.join(results))
                )
        )

        await self.send_message(
            message.channel,
            response,
            delete_after = 30
        )
