from collections import deque

class SongQueue(deque):

    def user_songs(self, user_id):
        return SongQueue(filter(
            lambda song: song.user_id == user_id,
            self
        ))

    def formatted(self):
        message = str()
        for i, song in enumerate(self):
            if i >= 10:
                message += '... and more'
                break
            message += '[{}] -- {} added by {}\n'.format(
                i + 1,
                song.formatted(),
                song.message.author.mention
            )
        return message


class RandomQueue(SongQueue):

    def formatted(self):
        header = '**{} backup song{}**'.format(
            len(self),
            '' if len(self) == 1 else 's'
        )
        return '{}\n{}'.format(header, super().formatted())
