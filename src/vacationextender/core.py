import json
import re
import heapq
import toml
import bisect

from datetime import date, timedelta
from typing import Dict, Any, List, Tuple, Union
from .mycalendar import Calendar, Break


class VacationExtender:
    def __init__(self, config_file: str = None, config_data: dict = None):
        if config_data:
            self.config = config_data
        else:
            self.config = self._load_config(config_file)
        self._process_config()
        self.breaks = list()
        self.selected_breaks = list()

    def __str__(self):
        """Returns all selected vacation bridges in a table."""
        # --- Formatting config ---
        N_SEP = 80
        HEADER_FORMAT = "{:<12} {:<12} {:<12} {:<12} {:>6} {:>6} {:>10}\n"
        ROW_FORMAT = "{:<12} {:<12} {:<12} {:<12} {:>6} {:>6} {:>10.2f}\n"
        SEPARATOR = "-" * N_SEP + '\n'

        ret = ''
        for i, selected_break in enumerate(self.selected_breaks[:self._top_n]):
            ret += "\n" + "=" * N_SEP + '\n'
            if self.algorithm == 'greedy' or self._top_n == 1:
                ret += f"🌴 EXTENDED VACATION 📅\n"
            else:
                ret += f"🌴 EXTENDED VACATION (suggestion {i + 1}) 📅\n"
            ret += "=" * N_SEP + '\n'

            ret += HEADER_FORMAT.format("BEGIN BREAK", "END BREAK",
                                        "BEGIN PTO", "END PTO",
                                        "PTO", "TOTAL", "ROI")
            ret += SEPARATOR

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
                    #br.w_roi
                )

                total_pto_used += br.days_pto
                total_days_gained += br.total

            ret += SEPARATOR

            ret += f"USED PTO: {total_pto_used} / {self.days}\n"
            ret += f"TOTAL BREAK DAYS: {total_days_gained}\n"
            ret += f"AVERAGE ROI: {total_days_gained / total_pto_used:.2f} break days / PTO days\n"
            ret += "=" * N_SEP + '\n'

        if len(ret) == 0:
            ret = 'No possible vacation that follows all conditions chosen!'
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

    def export_config(self, file_path: str = 'config.json'):
        json.dump({
            "CALENDAR": {
                "year": self.year,
                "weekend": self.weekend},
            "LOCATION": {
                "country_code": self.country,
                "subdivision_code": self.state,
                "include_observed": self.weekend_holiday},
            "CONSTRAINTS": {
                "vacation_days": self.days,
                "max_vac_periods": self.n_breaks,
                "in_holiday_as_pto": self.holiday_as_pto,
                "min_total_days_off": self.min_tot_break,
                "max_total_days_off": self.max_tot_break,
                "min_vac_days_per_break": self.min_vac_break,
                "max_vac_days_per_break": self.max_vac_break,
                "min_gap_days": self.min_gap,
                "top_n_suggestions": self.top_n,
                "custom_holidays": self.custom_holidays,
                "forced_work": self.forbidden,
                "must_be_vacation": self.must_be,
                "must_start_on": self.start_days,
                "must_end_on": self.end_days,
                "required_months": self.months
            },
            "ALGORITHM": {
                "algorithm_type": self.algorithm
            }
        }, open(file_path, 'w'), indent=4, default=str)

    def _str2date(self, dates: List[Union[str, date]]) -> List[date]:
        pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}):?(\d{4}-\d{2}-\d{2})?')
        all_dates = []
        for item in dates:
            if isinstance(item, date):
                all_dates.append(item)
                continue
            clean_item = str(item).strip().replace(" ", "")
            match = pattern.search(clean_item)
            if match:
                try:
                    date1 = date.fromisoformat(match.group(1))
                    d2_str = match.group(2)
                    if d2_str:
                        date2 = date.fromisoformat(d2_str)
                        start, end = sorted((date1, date2))
                        curr = start
                        while curr <= end:
                            all_dates.append(curr)
                            curr += timedelta(days=1)
                    else:
                        all_dates.append(date1)
                except Exception as err:
                    print(f"⚠️ WARNING: Invalid date value: '{item}' ({err})")
            else:
                print(f"⚠️ WARNING: Unrecognized format: '{item}'. Expected 'YYYY-MM-DD' or 'YYYY-MM-DD:YYYY-MM-DD'")
        return all_dates

    def _process_config(self):
        calendar = self.config.get('calendar', dict())
        today = date.today()
        self.year = calendar.get('year', today.year + 1)
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
        self.max_tot_break = constraints.get('max_total_days_off', 999999)
        if self.max_tot_break <= 0:
            self.max_tot_break = 999999
        self.holiday_as_pto = constraints.get('in_holiday_as_pto', False)
        self.min_gap = constraints.get('min_gap_days', 0)
        self._top_n = constraints.get('top_n_suggestions', 1)
        self.top_n = self._top_n * 5
        self.custom_holidays = constraints.get('custom_holidays', list())
        self.custom_holidays = self._str2date(self.custom_holidays)
        self.forbidden = constraints.get('forced_work', list())
        self.forbidden = self._str2date(self.forbidden)
        self.forbidden = set(self.forbidden)
        self.calendar = Calendar(self.country, self.state,
                                 first_day, last_day,
                                 self.weekend, self.custom_holidays,
                                 self.forbidden)
        self.must_be = constraints.get('must_be_vacation', list())
        self.must_be = self._str2date(self.must_be)
        self.start_days = constraints.get('must_start_on', list())
        self.start_days = self._str2date(self.start_days)
        self.start_days.sort()
        self.must_be.extend(self.start_days)
        self.end_days = constraints.get('must_end_on', list())
        self.end_days = self._str2date(self.end_days)
        self.end_days.sort()
        self.must_be.extend(self.end_days)
        self.must_be = list(sorted(set(self.must_be)))
        self.months = constraints.get('required_months', list())
        self.months = list(sorted(set(self.months)))
        algorithm = self.config.get('ALGORITHM', dict())
        self.algorithm = algorithm.get('algorithm', 'optimal')
        self.alpha = algorithm.get('duration_weight_factor_alpha', 0.5)

    def run(self):
        self._preprocess()
        if self.algorithm == 'optimal':
            self.breaks = list(sorted(br[-1] for br in self.breaks))
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

        for i in range(len(self.start_days)):
            while self.start_days[i] - dDay in self.calendar \
                    and self.calendar[self.start_days[i] - dDay].is_holiday():
                self.start_days[i] -= dDay

        for i in range(len(self.end_days)):
            while self.end_days[i] + dDay in self.calendar \
                    and self.calendar[self.end_days[i] + dDay].is_holiday():
                self.end_days[i] += dDay

        # day, steps, test next day is working day
        process_list = [(h, [-1, 1], True) for h in self.calendar.holidays()]
        process_list += [(d, [1], False) for d in self.start_days]
        process_list += [(d, [-1], False) for d in self.end_days]
        for beg_day, steps, test_working in process_list:
            if beg_day not in self.calendar:
                continue
            # Days before and after
            for f in steps:
                day = beg_day + f * dDay
                if day not in self.calendar:
                    br = self.calendar.new_break(
                        beg_day, beg_day,
                        self.holiday_as_pto,
                        self.alpha
                    )
                    if br is not None:
                        self.pq_add(br)
                    break
                if (not test_working) \
                        or self.calendar[day].is_working():
                    while day in self.calendar:
                        if self.calendar[day].is_forbidden():
                            break
                        break_lims = (
                            min(beg_day, day),
                            max(beg_day, day)
                        )
                        br = self.calendar.new_break(
                            break_lims[0], break_lims[1],
                            self.holiday_as_pto,
                            self.alpha
                        )
                        if br is None:
                            day += f * dDay
                            continue
                        if br.days_pto > self.days:
                            break
                        if br.days_pto > self.max_vac_break:
                            break
                        if br.days_pto < self.min_vac_break:
                            day += f * dDay
                            continue
                        if br.total < self.min_tot_break:
                            day += f * dDay
                            continue
                        if br.total > self.max_tot_break:
                            break
                        self.pq_add(br)
                        day += f * dDay

    def _prev_break(self, i, all_ends):
        max_date = self.breaks[i].begin.date() - timedelta(days=self.min_gap)
        return bisect.bisect_left(all_ends, max_date)

    def _check_valid(self, new_path: List[Break]) -> bool:
        if not new_path:
            return True
        br = new_path[-1]
        still = self.n_breaks - len(new_path)
        for must_be_i in self.must_be:
            if must_be_i > br.end.date():
                break
            if all(must_be_i not in b for b in new_path):
                return False
        for i, start_i in enumerate(self.start_days):
            if start_i > br.end.date():
                if still < len(self.start_days) - i:
                    return False
                break
            if all(start_i != b.begin.date() for b in new_path):
                return False
        for i, end_i in enumerate(self.end_days):
            if end_i > br.end.date():
                if still < len(self.end_days) - i:
                    return False
                break
            if all(end_i != b.end.date() for b in new_path):
                return False
        for i, month in enumerate(self.months):
            if month > br.end.date().month:
                if still < len(self.months) - i:
                    return False
                break
            month_satisfied = any(month == b.begin.date().month
                                  and month == b.end.date().month
                                  for b in new_path)
            if not month_satisfied:
                if month < br.begin.date().month:
                    return False
                if still == 0:
                    return False
        return True

    def _run_optimal(self):
        """ Runs the optimal vacation algorithm. """
        all_ends: List[date] = [b.end.date() for b in self.breaks]
        n = len(self.breaks)
        dp: List[List[List[List[Tuple[int, List[Break]]]]]] = \
            [[[[] for _ in range(self.n_breaks + 1)]
              for _ in range(self.days + 1)]
             for _ in range(n + 1)]
        for i in range(n + 1):
            for p in range(self.days + 1):
                dp[i][0][0] = [(0, [])]
        for i_idx, br in enumerate(self.breaks):
            i = i_idx + 1
            prev_idx = self._prev_break(i_idx, all_ends)

            for p in range(self.days + 1):
                for k in range(1, self.n_breaks + 1):
                    candidates = []
                    if dp[i - 1][p][k]:
                        prev_solutions = dp[i - 1][p][k]
                        for score, path in prev_solutions:
                            if self._check_valid(path):
                                candidates.append((score, path))
                    if p >= br.days_pto:
                        prev_solutions = dp[prev_idx][p - br.days_pto][k - 1]
                        for score, path in prev_solutions:
                            new_score = score + br.total
                            new_path = path + [br]
                            if self._check_valid(new_path):
                                candidates.append((new_score, new_path))
                    if candidates:
                        candidates.sort(key=lambda x: x[0], reverse=True)
                        dp[i][p][k] = candidates[:self.top_n]

        final_solutions = dp[n][self.days][self.n_breaks]
        self.selected_breaks = [sol[1] for sol in final_solutions]

    def _run_greedy(self):
        """ Runs the greedy vacation algorithm. """
        days_left = self.days
        curr: List[Break] = []
        ch_tried: bool = False
        while len(self.breaks) > 0 and days_left > 0:
            br: Break = self.pq_pop()
            if len(curr) > 0 and curr[-1].times_tried == br.times_tried - 1:
                if ch_tried:
                    break
                curr[-1].times_tried += 1
                ch_tried = True
                self.pq_add(curr[-1])
                self.selected_breaks.append(curr.copy())
                curr.pop()
            elif len(curr) == self.n_breaks - 1 \
                    and br.days_pto != days_left:
                ch_tried = False
                self.pq_add(br)
            elif br.days_pto > days_left \
                    or any(br ^ ci for ci in curr) \
                    or any(br.gap(ci) < self.min_gap for ci in curr):
                ch_tried = False
                self.pq_add(br)
            else:
                ch_tried = False
                curr.append(br)
                days_left -= br.days_pto
        self.selected_breaks.append(curr.copy())
