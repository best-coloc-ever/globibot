from gtts import gTTS

from tempfile import mktemp
from collections import defaultdict

LANGUAGES = (
    ('af', 'afrikaans'), ('sq', 'albanian'), ('ar', 'arabic'),
    ('hy', 'armenian'), ('bn', 'bengali'), ('ca', 'catalan'), ('zh', 'chinese'),
    ('zh-cn', 'chinese (mandarin/china)'),
    ('zh-tw', 'chinese (mandarin/taiwan)'), ('zh-yue', 'chinese (cantonese)'),
    ('hr', 'croatian'), ('cs', 'czech'), ('da', 'danish'), ('nl', 'dutch'),
    ('en', 'english'), ('en-au', 'english (australia)'),
    ('en-uk', 'english (united kingdom)'), ('en-us', 'english (united states)'),
    ('eo', 'esperanto'), ('fi', 'finnish'), ('fr', 'french'), ('de', 'german'),
    ('el', 'greek'), ('hi', 'hindi'), ('hu', 'hungarian'), ('is', 'icelandic'),
    ('id', 'indonesian'), ('it', 'italian'), ('ja', 'japanese'),
    ('ko', 'korean'), ('la', 'latin'), ('lv', 'latvian'), ('mk', 'macedonian'),
    ('no', 'norwegian'), ('pl', 'polish'), ('pt', 'portuguese'),
    ('pt-br', 'portuguese (brazil)'), ('ro', 'romanian'), ('ru', 'russian'),
    ('sr', 'serbian'), ('sk', 'slovak'), ('es', 'spanish'),
    ('es-es', 'spanish (spain)'), ('es-us', 'spanish (united states)'),
    ('sw', 'swahili'), ('sv', 'swedish'), ('ta', 'tamil'), ('th', 'thai'),
    ('tr', 'turkish'), ('vi', 'vietnamese'), ('cy', 'welsh'),
)

DEFAULT_LANGUAGE = 'en-us'

LANGUAGES_BY_SYMBOLS = dict(LANGUAGES)
SYMBOLS_BY_LANGUAGES = dict((lang, sym) for sym, lang in LANGUAGES)

def make_tts_file(content, lang):
    fp = mktemp()

    tts = gTTS(text=content, lang=lang)
    tts.save(fp)

    return fp

class TTSManager:

    def __init__(self):
        self.server_languages = defaultdict(lambda: DEFAULT_LANGUAGE)

    def set_server_language(self, server, lang):
        if lang in LANGUAGES_BY_SYMBOLS:
            sym = lang
        elif lang in SYMBOLS_BY_LANGUAGES:
            sym = SYMBOLS_BY_LANGUAGES[lang]
        else:
            return False

        self.server_languages[server.id] = sym
        return True

    def talk_in(self, server, content, lang=None):
        lang = lang or self.server_languages[server.id]
        return make_tts_file(content, lang)
