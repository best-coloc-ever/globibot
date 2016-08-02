def format_seconds(seconds):
    return '{:02d}:{:02d}'.format(
        int(seconds / 60),
        int(seconds % 60)
    )

KEWL_MAGIC = 8419

def format_kewl_number(i):
    s = '{}'.format(i)
    return ''.join([c + chr(KEWL_MAGIC) for c in s])

def elided(s, size):
    if len(s) <= size:
        return s
    else:
        return '{}...'.format(s[size - 3:])
