#! /usr/bin/env python3
import os.path
import sys
from datetime import datetime, timedelta
from enum import Enum

DATE_FORMAT = "%y.%m.%d"
TIME_FORMAT = "%H:%M:%S"


class Stamp(Enum):
    ARRIVE = 'ARRIVE'
    LEAVE = "LEAVE"


class TimeTable:
    storage = {}
    today = None

    def set_today(self, today: str):
        self.today = today

    def add_entry(self, day: str, stamp: Stamp, time: datetime):
        if self.storage.get(day) is None:
            self.storage[day] = {Stamp.ARRIVE: [], Stamp.LEAVE: []}
        self.storage[day][stamp].append(time)

    def start_of_day(self):
        if stamps := self.storage.get(self.today):
            return min(stamps[Stamp.ARRIVE])
        return None

    def end_of_day(self):
        if stamps := self.storage.get(self.today):
            return max(stamps[Stamp.LEAVE])
        return None

    def whole_day(self):
        start = self.start_of_day()
        end = self.end_of_day()

        if not start and end:
            return None
        return end - start

    def _first_entry_after(self, kind: Stamp, time: datetime):
        entries = self.storage[self.today][kind]
        for entry in entries:
            if entry > time:
                return entry
        return None

    def breaks(self):
        last = self.end_of_day()
        breaks = []
        start = self._first_entry_after(Stamp.LEAVE, self.start_of_day())
        if start == last:
            return []

        def loop(start):
            end_of_break = self._first_entry_after(Stamp.ARRIVE, start)
            breaks.append((start, end_of_break))
            new_start = self._first_entry_after(Stamp.LEAVE, end_of_break)
            if new_start == last:
                return breaks
            return loop(new_start)

        return loop(start)

    def break_time(self):
        breaks = self.breaks()
        sum = timedelta()
        for (start, end) in self.breaks():
            sum += end - start
        return sum


time_table = TimeTable()


with open(os.path.join(os.path.dirname(__file__), "table")) as file:
    for line in file.readlines():
        kind, date, time = line.split()
        stamp = Stamp[kind]
        date_time = datetime.strptime(time, TIME_FORMAT)
        time_table.add_entry(date, stamp, date_time)
try:
    today = sys.argv[1]
except IndexError:
    today = datetime.now().strftime("%d.%m.%y")

time_table.set_today(today)

print("arraived at: ", time_table.start_of_day())
print("left at: ", time_table.end_of_day())
print("break time: ", time_table.break_time())
