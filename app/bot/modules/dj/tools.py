def format_seconds(seconds):
    return '{:02d}:{:02d}'.format(
        int(seconds / 60),
        int(seconds % 60)
    )
