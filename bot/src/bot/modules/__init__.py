from .hello.module import Hello
from .twitch.module import Twitch
from .twitter.module import Twitter
from .dj.module import Dj
from .giveaway.module import Giveaway
from .github.module import Github
from .eval.module import Eval

from utils.logging import logger

MODULE_CLASSES_BY_NAME = {
    'hello'   : Hello,
    'twitch'  : Twitch,
    'twitter' : Twitter,
    'dj'      : Dj,
    'giveaway': Giveaway,
    'github'  : Github,
    'eval'    : Eval,
}

def module_class_by_name(name):
    try:
        return MODULE_CLASSES_BY_NAME[name.lower()]
    except KeyError:
        logger.warning('No module named: {} (Ignoring...)'.format(name))
