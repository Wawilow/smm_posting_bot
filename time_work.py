import datetime
import time as times


class Time:
    def __init__(self):
        self.time = None
        self.unix_time = None

    def time_now(self):
        self.time = datetime.datetime.now()
        return self.time

    def delta_time(self, delta_days=0, delta_hours=0, delta_minutes=0):
        delta = datetime.timedelta(days=delta_days, hours=delta_hours, minutes=delta_minutes)
        if type(self.time) is list:
            if len(self.time) == 3:
                self.self.time = datetime.date(*self.time) + delta
                return self.time
            elif len(self.time) == 6:
                self.time = datetime.datetime(*self.time) + delta
                return self.self.time
        elif type(self.time) is datetime.date or type(self.time) is datetime.datetime:
            self.time = self.time + delta
            return self.time + delta

    def replace_time(self, year=False, month=False, day=False, hour=False, minute=False, second=False):
        if type(self.time) is datetime.datetime or type(self.time) is datetime.date:
            if year:
                self.time = self.time.replace(year=year)
            if month:
                self.time = self.time.replace(month=month)
            if day:
                self.time = self.time.replace(day=day)
        if type(self.time) is datetime.datetime:
            if hour:
                self.time = self.time.replace(hour=hour)
            if minute:
                self.time = self.time.replace(minute=minute)
            if second:
                self.time = self.time.replace(second=second)
        return self.time

    def unix_time_convert(self):
        if type(self.time) is datetime.datetime or type(self.time) is datetime.date:
            self.unix_time = int(times.mktime(self.time.timetuple()))
        return (self.unix_time)

    def datatime_convert(self):
        if self.time is None and type(self.unix_time) is int:
            self.time = datetime.datetime.fromtimestamp(self.unix_time)
            return self.time


if __name__ == '__main__':
    pass