from youtube_dl import YoutubeDL

from .errors import YTDLExtractInfosError

from . import constants as c
from . import tools as t

class Song:

    def __init__(self, link, message):
        self.link = link
        self.message = message
        self.user_id = message.author.id

        self._fetch_infos()

    def _fetch_infos(self):
        try:
            ydl = YoutubeDL(c.YTDL_OPTIONS)
            info = ydl.extract_info(self.link, download=False)

            self.title = info['title']
            self.views = info['view_count']
            self.likes = info['like_count']
            self.dislikes = info['dislike_count']
            self.duration = info['duration']
        except Exception as e:
            raise YTDLExtractInfosError(e)

    def formatted(self):
        return (
            '**{}** (`{}`) [`{}` **views** / `{}` 👍 / `{}` 👎]'
        ).format(
            self.title,
            t.format_seconds(self.duration),
            self.views,
            self.likes,
            self.dislikes
        )

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.title == other.title
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.title)
