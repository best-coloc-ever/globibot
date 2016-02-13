from . import tools as t

from collections import deque

class SongQueue(deque):

    def user_songs(self, user_id):
        return SongQueue(filter(
            lambda song: song.user_id == user_id,
            self
        ))

    def __str__(self):
        if len(self) == 0:
            return 'No queue'
        else:
            s = '\n------------- **CURRENT QUEUE** -------------\n\n'
            songs = [self.song_str(song, i + 1) for i, song in enumerate(list(self)[:9])]
            s += '\n'.join(songs)
            if len(self) > 10:
                s += '\n... and {} more'.format(len(self) - 9)
            return s

    def song_str(self, song, pos):
        return '{pos}\t{song:80}\tAdded by {who}'.format(
            pos=t.format_kewl_number(pos),
            song=t.elided(str(song), 80),
            who=song.message.author.name
        )


class RandomQueue(SongQueue):

    def __str__(self):
        return (
            '--------------------------------------------------\n'
            '⚠ *No song in queue* ⚠\n'
            '*Playing songs from the past*\n'
            '{}'
        ).format(
            super().__str__()
        )
