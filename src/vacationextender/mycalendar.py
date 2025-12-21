import holidays as hd
from datetime import date, timedelta
from typing import List, Set, Union, Dict, Optional

FORBIDDEN, HOLIDAY, WORKING = range(3)
TYPES = {0: 'forbidden',
         1: 'holiday',
         2: 'working'}
dDAY = timedelta(days=1)


class CalendarDay:
    def __init__(self, day: date):
        self.day: date = day
        self.type: int = WORKING

    def __str__(self):
        return f'{self.day} {TYPES[self.type]}'

    def __gt__(self, other):
        if isinstance(other, date):
            return self.day > other
        return self.day > other.day

    def __lt__(self, other):
        if isinstance(other, date):
            return self.day < other
        return self.day < other.day

    def __eq__(self, other):
        if isinstance(other, date):
            return self.day == other
        return self.day == other.day

    def __ge__(self, other):
        if isinstance(other, date):
            return self.day >= other
        return self.day >= other.day

    def __le__(self, other):
        if isinstance(other, date):
            return self.day <= other
        return self.day <= other.day

    def set_forbidden(self):
        self.type = FORBIDDEN

    def set_holiday(self):
        self.type = HOLIDAY

    def set_working(self):
        self.type = WORKING

    def date(self) -> date:
        return self.day

    def is_holiday(self) -> bool:
        return self.type == HOLIDAY

    def is_working(self) -> bool:
        return self.type == WORKING

    def is_forbidden(self) -> bool:
        return self.type == FORBIDDEN

    def strftime(self, format: str) -> str:
        return self.day.strftime(format)


class Calendar:
    def __init__(self, country: str = 'BR', subdivision: str = None,
                 first_date: Union[date, CalendarDay] = None,
                 last_date: Union[date, CalendarDay] = None,
                 weekend: List[int] = None,
                 custom_holidays: List[Union[date, CalendarDay]] = None,
                 forbidden: Set[Union[date, CalendarDay]] = None):
        self.country: str = country
        self.state: str = subdivision
        if first_date is None:
            first_date = date(date.today().year, 1, 1)
        if last_date is None:
            last_date = date(date.today().year, 12, 31)
        self.first_date = CalendarDay(first_date)
        self.last_date = CalendarDay(last_date)
        self.weekends: List[int] = [5, 6] if weekend is None else weekend
        self.dates: Dict[date, CalendarDay] = dict()
        self.years: Set[int] = set()
        curr = self.first_date.date()
        while curr <= self.last_date.date():
            self.dates[curr] = CalendarDay(curr)
            self.years.add(curr.year)
            curr += dDAY
        self._load_holidays()
        self._holidays.extend(custom_holidays)
        self._forbidden = forbidden
        for curr in self.dates:
            if curr in forbidden:
                self.dates[curr].set_forbidden()
            elif self.is_weekend(curr):
                self.dates[curr].set_holiday()
                self._holidays.append(curr)
            elif self.is_holiday(curr):
                self.dates[curr].set_holiday()
        self._holidays.sort()

    def __str__(self):
        return '\n'.join(str(day) for day in self)

    def __iter__(self):
        self._iter_current_date = self.first_date.date()
        return self

    def __next__(self) -> CalendarDay:
        if self._iter_current_date > self.last_date.date():
            raise StopIteration
        current_day: CalendarDay = self.dates.get(self._iter_current_date)

        if current_day is None:
            raise ValueError(f"Day {self._iter_current_date} ausente no calendário.")
        self._iter_current_date += timedelta(days=1)
        return current_day

    def __getitem__(self, item: Union[int, date]) -> CalendarDay:
        if isinstance(item, int):
            return self.dates[self.first_date.date() + timedelta(days=item)]
        return self.dates[item]

    def __contains__(self, item: date):
        return self.first_date.date() <= item <= self.last_date.date()

    def _load_holidays(self):
        """
        Loads all holidays in the specified year and location.
        """
        try:
            self._holidays = list(sorted(hd.country_holidays(
                country=self.country,
                subdiv=self.state,
                years=self.years,
                observed=True
            ).keys()))
        except Exception as err:
            raise ValueError(
                f"Error loading holidays from {self.country}/{self.state} in the years {self.years}. '"
                f"Details: {err}")

    def holidays(self):
        if self._holidays is None:
            self._load_holidays()
        return self._holidays

    def is_weekend(self, day: date) -> bool:
        return self.dates[day].date().weekday() in self.weekends

    def is_holiday(self, day: date) -> bool:
        return self.dates[day].date() in self.holidays()

    def is_working(self, day: date) -> bool:
        return not (self.is_weekend(day) or self.is_holiday(day))

    def new_break(self, begin: date, end: date,
                  in_holiday_as_pto: bool, alpha: float):
        while begin - dDAY in self and self[begin - dDAY].is_holiday():
            begin -= dDAY
        while end + dDAY in self and self[end + dDAY].is_holiday():
            end += dDAY
        br = Break(begin, end, alpha)
        n_total = (end - begin).days + 1
        n_holiday = 0
        while begin in self and self[begin].is_holiday() and begin <= end:
            n_holiday += 1
            begin += dDAY
        while end in self and self[end].is_holiday() and end >= begin:
            n_holiday += 1
            end -= dDAY
        br.set_pto_range(begin, end)
        if not in_holiday_as_pto:
            while begin <= end:
                if self[begin].is_holiday():
                    n_holiday += 1
                begin += dDAY
        n_pto = n_total - n_holiday
        if n_pto == 0:
            return
        br.set_days(n_pto, n_holiday)
        return br


class Break:
    def __init__(self, begin: date, end: date, alpha: float):
        self.begin = CalendarDay(begin)
        self.end = CalendarDay(end)
        self.begin_pto = None
        self.end_pto = None
        self.days_pto: Optional[int] = None
        self.days_holidays: Optional[int] = None
        self.total: Optional[int] = None
        self.roi: Optional[int] = None
        self.w_roi: Optional[int] = None
        self.times_tried: int = -1
        self.alpha = alpha

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

    def __lt__(self, other) -> bool:
        if self.end != other.end:
            return self.end < other.end
        return self.begin < other.begin

    def __xor__(self, other):
        return self.gap(other) == 0

    def __contains__(self, item: Union[date, CalendarDay]) -> bool:
        return self.begin <= item <= self.end

    def gap(self, other):
        if self.end < other.begin:
            return (other.begin.date() - self.end.date()).days
        if self.begin > other.end:
            return (self.begin.date() - other.end.date()).days
        return 0

    def set_pto_range(self, begin: date, end: date):
        self.begin_pto, self.end_pto = CalendarDay(begin), CalendarDay(end)

    def set_days(self, pto: int, holidays: int):
        self.days_pto = pto
        self.days_holidays = holidays
        self.total = self.days_pto + self.days_holidays
        self.roi = self.total / self.days_pto
        self.w_roi = self.total ** (1 + self.alpha) / self.days_pto
