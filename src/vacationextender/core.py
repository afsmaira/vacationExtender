import heapq
import toml
from datetime import date, timedelta
from typing import Dict, Any, List, Tuple, Union
from .mycalendar import Calendar, Break


class VacationExtender:
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self._process_config()
        self.breaks = list()
        self.selected_breaks = list()

    def __str__(self):
        """Returns all selected vacation bridges in a table."""

        ret = ''
        for i, selected_break in enumerate(self.selected_breaks):
            # --- Formatting config ---
            N_SEP = 90
            HEADER_FORMAT = "{:<12} {:<12} {:<12} {:<12} {:>6} {:>6} {:>10} {:>10}\n"
            ROW_FORMAT = "{:<12} {:<12} {:<12} {:<12} {:>6} {:>6} {:>10.2f} {:>10.2f}\n"
            SEPARATOR = "-" * N_SEP + '\n'

            ret = "\n" + "=" * N_SEP + '\n'
            if self.algorithm == 'greedy':
                ret += f"🌴 EXTENDED VACATION 📅\n"
            else:
                ret += f"🌴 EXTENDED VACATION (option {i+1}) 📅\n"
            ret += "=" * N_SEP + '\n'

            # Headers
            ret += HEADER_FORMAT.format("BEGIN BREAK", "END BREAK",
                                        "BEGIN PTO", "END PTO",
                                        "PTO", "TOTAL", "ROI", "SCORE")
            ret += SEPARATOR

            # Impressão das linhas
            total_pto_used = 0
            total_days_gained = 0

            for br in selected_break:
                start_date_str = br.begin.strftime("%Y-%m-%d")
                end_date_str = br.end.strftime("%Y-%m-%d")
                start_date_pto_str = br.begin_pto.strftime("%Y-%m-%d")
                end_date_pto_str = br.end_pto.strftime("%Y-%m-%d")

                ret += ROW_FORMAT.format(
                    start_date_str,
                    end_date_str,
                    start_date_pto_str,
                    end_date_pto_str,
                    br.days_pto,
                    br.total,
                    br.roi,
                    br.w_roi
                )

                total_pto_used += br.days_pto
                total_days_gained += br.total

            ret += SEPARATOR

            # Resumo Final
            ret += f"USED PTO: {total_pto_used} / {self.days}\n"
            ret += f"TOTAL BREAK DAYS: {total_days_gained}\n"
            ret += f"AVERAGE ROI: {total_days_gained / total_pto_used:.2f} break days / PTO days\n"
            ret += "=" * N_SEP + '\n'

        return ret

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

    def pq_add(self, br: Break):
        br.times_tried += 1
        item = (br.times_tried,
                -br.w_roi, -br.total, br.days_pto, br
                )
        if item not in self.breaks:
            heapq.heappush(self.breaks, item)

    def pq_pop(self):
        return heapq.heappop(self.breaks)[-1]

    def _preprocess(self):
        """ Preprocesses the data. """
        dDay = timedelta(days=1)
        for holiday in self.calendar.holidays():
            # Days before and after
            for f in [-1, 1]:
                pto_day = holiday + f * dDay
                if pto_day in self.calendar\
                    and self.calendar[pto_day].is_working():
                    break_lim1, n_holiday = holiday, 1
                    while break_lim1-f*dDay in self.calendar\
                        and self.calendar[break_lim1-f*dDay].is_holiday():
                        break_lim1 -= f*dDay
                        n_holiday += 1
                    break_lim2, n_pto = pto_day, 1
                    while break_lim2+f*dDay in self.calendar\
                        and not self.calendar[break_lim2+f*dDay].is_forbidden():
                        break_lim2 += f*dDay
                        if self.holiday_as_pto:
                            n_pto += 1
                        elif self.calendar[break_lim2].is_working():
                            n_pto += 1
                        elif self.calendar[break_lim2].is_holiday():
                            n_holiday += 1
                        if n_pto > self.max_vac_break:
                            break
                        if n_pto >= self.min_vac_break\
                            and n_pto + n_holiday >= self.min_tot_break:
                            break_lims = (
                                min(break_lim1, break_lim2),
                                max(break_lim1, break_lim2)
                            )
                            self.pq_add(self.calendar.new_break(*break_lims,
                                                                self.holiday_as_pto,
                                                                self.alpha))

    def _run_optimal(self):
        """ TODO: Runs the optimal vacation algorithm. """
        # TODO: many greedy
        pass

    def _run_greedy(self):
        """ Runs the greedy vacation algorithm. """
        days_left = self.days
        curr: List[Break] = []
        ch_tried: bool = False
        while len(self.breaks) > 0 and days_left > 0:
            br = self.pq_pop()
            if len(curr) > 0 and curr[-1].times_tried == br.times_tried-1:
                if ch_tried:
                    break
                curr[-1].times_tried += 1
                ch_tried = True
                self.pq_add(curr[-1])
                self.selected_breaks.append(curr.copy())
                curr.pop()
            elif len(curr) == self.n_breaks-1\
                and br.days_pto != days_left:
                ch_tried = False
                self.pq_add(br)
            elif br.days_pto > days_left\
                or any(br ^ ci for ci in curr):
                ch_tried = False
                self.pq_add(br)
            else:
                ch_tried = False
                curr.append(br)
                days_left -= br.days_pto
        self.selected_breaks.append(curr.copy())
