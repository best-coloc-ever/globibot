from datetime import datetime, timedelta
from globibot.lib.helpers import parsing as p
from math import floor

TIMEZONES = { 'UTC', 'PDT', 'EDT', 'BST', 'CEST', 'EEST' }

OFFSETS = {
    'UTC': 0,
    'PDT': -7,
    'EDT': -4,
    'BST': +1,
    'CEST': +2,
    'EEST': +3,
}

hour_parser = p.int_range(0, 24) | p.string('midnight') >> (lambda t: 0) | p.string('noon') >> (lambda t: 12)
minutes_parser = p.skip(p.one_of(p.string, 'h', ':', '.')) + p.int_range(0, 60)
meridiem_parser = p.one_of(p.string, 'am', 'pm') >> p.to_s
tz_parser = p.one_of(p.string, *TIMEZONES) >> p.to_s

time_parser = (
    hour_parser +
    p.maybe(minutes_parser) +
    p.maybe(meridiem_parser) +
    p.maybe(tz_parser)
)

class Time:

    def __init__(self, h, m, meridiem, tz):
        self.h = h
        self.m = m or 0
        self.meridiem = meridiem
        self.tz = tz or 'UTC'

    def countdown(self):
        now = datetime.utcnow()
        then = now.replace(hour=self.real_h, minute=self.m)
        offset = OFFSETS.get(self.tz.upper(), 0)
        then -= timedelta(hours=offset)
        time_diff = then - now
        seconds = round(time_diff.total_seconds())
        print(seconds)
        while seconds < 0:
            seconds += 24 * 60 * 60
        minutes = round(seconds / 60)

        return (floor(minutes / 60), minutes % 60)

    def __str__(self):
        h, m = self.countdown()
        countdown_string = 'in ~ {:02}:{:02}'.format(h, m) if h + m != 0 else 'now'
        return '{:02}:{:02}{} {} is {}'.format(
            self.h, self.m,
            ' {}'.format(self.meridiem) if self.meridiem else '',
            self.tz.upper(),
            countdown_string
        )

    TIME_TABLE_TEMPLATE = (
        '       North America       |                   Europe                    \n'
        ' ----------- | ----------- | ------------------------------------------  \n'
        ' West (PDT)  |  East (EDT) | Brexit (BST) | Central (CEST) | East (EEST) \n'
        ' ----------- | ----------- | ------------ | -------------- | ----------  \n'
        ' {:^11} | {:^11} | {:^12} | {:^14} | {:^10} '
    )
    def timetable(self):
        offset = OFFSETS.get(self.tz.upper(), 0)
        utc_h = self.real_h - offset
        times = []
        for zone in ('PDT', 'EDT', 'BST', 'CEST', 'EEST'):
            z_offset = OFFSETS[zone]
            h = utc_h + z_offset
            h_12 = h if h <= 12 else h - 12
            if h_12 < 0:
                h_12 += 12
            meridiem = 'AM' if h >= 0 and h < 12 else 'PM'
            times.append('{:02}:{:02} {}'.format(h_12, self.m, meridiem))
        return Time.TIME_TABLE_TEMPLATE.format(*times)

    @property
    def real_h(self):
        if self.meridiem == 'pm':
            if self.h != 12:
                return self.h + 12

        if self.meridiem == 'am':
            if self.h == 12:
                return 0

        return self.h
