from datetime import datetime
from datetime import timedelta

class Timestamp:
    def __init__(self):
        self.ts = datetime.now()
        self._set_hm()

    def next(self):
        self.ts = self.ts + timedelta(seconds=1)
        self._set_hm()

    def _set_hm(self):
        self.hours = self.ts.strftime("%H")
        self.minutes = self.ts.strftime("%M")
        self.date = self.ts.strftime("%d.%m.%Y")
        self.day_of_week = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][
            self.ts.today().weekday()
        ]


def now():
    return Timestamp()

