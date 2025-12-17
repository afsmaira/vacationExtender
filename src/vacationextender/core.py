import os
import toml
from datetime import date, timedelta
from typing import Dict, List, Tuple, Union
from .mycalendar import Calendar

class VacationExtender:
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self._process_config()
        self.breaks = list()
        self.selected_breaks = list()

    def _load_config(self, file_path: str) -> Dict[str, Any]:
        """Reads and processes the configuration file (TOML format)."""
        if file_path is None:
            return dict()
        try:
            with open(file_path, 'r') as f:
                return toml.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found at: {file_path}")
        except toml.TomlDecodeError:
            raise Exception("Error decoding TOML file. Check syntax.")

    def _process_config(self):
        calendar = self.config.get('calendar', dict())
        today = date.today()
        self.year = calendar.get('year', today.year+1)
        first_day = max(today, date(self.year, 1, 1))
        last_day = date(self.year, 12, 31)
        self.weekend = calendar.get('weekend', [5, 6])
        location = self.config.get('LOCATION', dict())
        self.country = location.get('country_code', "BR")
        self.state = location.get('subdivision_code', "SP")
        self.weekend_holiday = location.get('include_observed', False)
        constraints = self.config.get('CONSTRAINTS', dict())
        self.days = constraints.get('vacation_days', 30)
        self.n_breaks = constraints.get('max_vac_periods', 3)
        self.max_vac_break = constraints.get('max_vac_days_per_break',
                                             self.days)
        if self.max_vac_break <= 0:
            self.max_vac_break = self.days
        self.min_vac_break = constraints.get('min_vac_days_per_break', 1)
        self.min_tot_break = constraints.get('min_total_days_off', 1)
        self.holiday_as_pto = constraints.get('in_holiday_as_pto', True)
        self.custom_holidays = constraints.get('custom_holidays', list())
        self.forbidden = constraints.get('forced_work_dates', list())
        forb_intervals = constraints.get('forced_work_intervals', list())
        for forb_interval in forb_intervals:
            beg = forb_interval['start']
            end = forb_interval['end']
            while beg <= end:
                self.forbidden.append(beg)
                beg += timedelta(days=1)
        self.forbidden = set(self.forbidden)
        self.calendar = Calendar(self.country, self.state,
                                 first_day, last_day,
                                 self.weekend, self.custom_holidays,
                                 self.forbidden)
        algorithm = self.config.get('ALGORITHM', dict())
        self.algorithm = algorithm.get('algorithm', 'greedy')
        self.alpha = algorithm.get('duration_weight_factor_alpha', 0.5)

    def run(self):
        self._preprocess()
        if self.algorithm == 'optimal':
            self._run_optimal()
        else:
            self._run_greedy()

    def _preprocess(self):
        """ Preprocesses the data. """
        # Days map (FORBIDDEN, HOLIDAY/WEEKEND, WORKING)
        for date in self.calendar:

        # TODO: Potential breaks (identifies all candidates; fora each bridge coast, beneficy, efficiency)

        pass

    def _run_optimal(self):
        """ TODO: Runs the optimal vacation algorithm. """
        # TODO: many greedy
        pass

    def _run_greedy(self):
        """ TODO: Runs the greedy vacation algorithm. """
        # TODO: Sort by efficiency (PQ)
        # TODO: Iterate (chose the most efficient, check conflict
        pass