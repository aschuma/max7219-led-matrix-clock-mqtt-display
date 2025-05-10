import re
from datetime import datetime
from datetime import timedelta

class Timestamp:
    def __init__(self, ts):
        self.ts = ts
        self._set_hm()

    def next(self):
        return Timestamp(ts = self.ts + timedelta(seconds=1))

    def _set_hm(self):
        self.hours = re.sub(r"^(0)(.)$", r" \2", self.ts.strftime("%H"))
        self.minutes = self.ts.strftime("%M")
        self.date = self.ts.strftime("%d.%m.%Y")
        self.weekday = self.ts.today().weekday()
        self.day_of_week = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][
            self.weekday
        ]

    @staticmethod
    def now():
        return Timestamp(datetime.now())

