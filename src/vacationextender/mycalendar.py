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
        return self.day > other.day

    def __eq__(self, other):
        return self.day == other.day

    def __ge__(self, other):
        return self.day >= other.day

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
            curr += timedelta(days=1)
        self.weekends: List[int] = [5, 6] if weekend is None else weekend
        self._load_holidays()

    def __iter__(self):
        self._iter_current_date = self.first_date
        return self

    def __next__(self) -> CalendarDay:
        if self._iter_current_date > self.last_date:
            raise StopIteration
        current_day: CalendarDay = self.dates.get(self._iter_current_date.date())

        if current_day is None:
            raise ValueError(f"Day {self._iter_current_date} ausente no calendário.")

        # 3. Prepara a data para a próxima chamada
        self._iter_current_date += timedelta(days=1)

        # 4. Retorna o objeto CalendarDay da iteração atual (a REFERÊNCIA)
        return current_day

    def __getitem__(self, item: Union[int, date]) -> CalendarDay:
        if isinstance(item, int):
            return self.dates[self.first_date.date() + timedelta(days=item)]
        return self.dates[item]

    def set_forbidden(self, days: Union[date, CalendarDay, Iterable[date], Iterable[CalendarDay]]):
        if isinstance(days, date):
            days = {days}
        if isinstance(days, CalendarDay):
            days = {days.date()}
        if isinstance(days, (list, set)):
            if len(days) == 0: return
            days = {day.date() if isinstance(day, CalendarDay)
                    else day for day in days}
        for day in days:
            self.dates[day].set_forbidden()

    def _load_holidays(self):
        """
        Loads all holidays in the specified year and location.
        """
        try:
            self._holidays = set(hd.country_holidays(
                country=self.country,
                subdiv=self.state,
                years=self.years,
                observed=True
            ).keys())
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
