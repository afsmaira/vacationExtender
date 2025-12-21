# 🌴 Vacation Extender 📅

![GitHub stars](https://img.shields.io/github/stars/afsmaira/vacationExtender?style=social)
[![PyPI version](https://img.shields.io/pypi/v/vacation-extender.svg)](https://pypi.org/project/vacation-extender/)
[![Python versions](https://img.shields.io/pypi/pyversions/vacation-extender.svg)](https://pypi.org/project/vacation-extender/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Maximize Your Time Off. Smartly connect public holidays and weekends for the longest possible vacations.**

---

## 🚀 Overview

VacationExtender is a smart scheduling program designed to optimize your annual leave. By analyzing public holidays and fixed weekend dates, it identifies the best days to take off, allowing you to **"bridge"** short working periods and create maximum-length holiday streaks from minimal paid time off.

Perfect for travelers, remote workers, and anyone looking to get the most value out of their vacation days!

## ✨ Key Features

* **Minimal PTO Usage:** Prioritizes solutions that yield the longest rest period for the lowest number of paid days used.
* **Localization Ready:** Easily adaptable to different countries' holiday calendars. (Default: Brazil).
* **Simple Output:** Provides clear date ranges and the resulting total days of vacation.

## 🛠️ Installation

Since the package is hosted on PyPI, installation is simple:

```bash
pip install vacation-extender
```

## ⚡ Quick Start

1.  **Generate a configuration file:**
    Create a default `config.toml` in your current folder.
    ```bash
    vacationext init
    ```

2.  **Edit the configuration file if needed.**

3.  **Run the optimizer:**
    ```bash
    vacationext
    ```
    *Or run with a specific config file:*
    ```bash
    vacationext --config your_config_file.toml
    ```

### Expected Output

The program will output a suggested schedule, such as:

```text
==========================================================================================
🌴 EXTENDED VACATION (option 1) 📅
==========================================================================================
BEGIN BREAK  END BREAK    BEGIN PTO    END PTO         PTO  TOTAL        ROI      SCORE
------------------------------------------------------------------------------------------
2026-02-14   2026-02-22   2026-02-19   2026-02-20        2      9       4.50      13.50
2026-10-31   2026-11-08   2026-11-05   2026-11-06        2      9       4.50      13.50
2026-11-20   2026-12-31   2026-11-23   2026-12-18       26     42       1.62      10.47
------------------------------------------------------------------------------------------
USED PTO: 30 / 30
TOTAL BREAK DAYS: 60
AVERAGE ROI: 2.00 break days / PTO days
==========================================================================================
```

## 🤝 Contribution

We welcome contributions! Whether it's adding a new country's holiday calendar, improving the optimization algorithm, or enhancing the documentation, your help is appreciated.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ⚙️ Configuration File (`config.toml`)

The `config.toml` file is the primary way to define the optimization parameters, including the target calendar, location, and user-specific PTO constraints. You can run the optimizer with a custom configuration file path using the command line (e.g., `vacationext --config config_us.toml`).

---

### 📅 `[CALENDAR]`

These parameters define the basic time structure for the optimization.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `year` | Integer | `2026` | The **target year** for which the vacation plan will be generated. |
| `weekend` | List of Integers | `[5, 6]` | Defines non-working days. **0** is Monday, **6** is Sunday. |

---

### 🌍 `[LOCATION]`

These settings tell the `VacationExtender` which public holiday calendar to load using the `holidays` library.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `country_code` | String | `"BR"` | The **ISO 3166-1 alpha-2 code** (e.g., "US", "DE", "BR"). |
| `subdivision_code` | String | `"SP"` | Optional code for state/province holidays. Use `""` for country-only holidays. |
| `include_observed` | Boolean | `false` | If holidays that fall on a weekend should be **shifted and observed** on the next weekday (common in the US). |

---

### 🚧 `[CONSTRAINTS]`

This section defines the user's budget and specific rules for suggesting optimal vacation periods.

| Parameter                | Type             | Default | Description                                                                                                                                                                |
|:-------------------------|:-----------------|:--------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `vacation_days`          | Integer          | `30`    | The **total PTO (Paid Time Off)** budget available for the year. The algorithm will stop when this budget is depleted.                                                     |
| `max_vac_periods`        | Integer          | `3`     | The maximum number of **separate vacation periods** (breaks) the algorithm should suggest.                                                                                 |
| `min_vac_days_per_break` | Integer          | `1`     | The minimum number of **PTO days** required to be used for a period to be considered a bridge suggestion.                                                                  |
| `max_vac_days_per_break` | Integer          | `-1`    | The maximum number of **PTO days** you are willing to spend for a single continuous break. Use `-1` for no limit.                                                          |
| `min_total_days_off`     | Integer          | `1`     | The minimum number of **TOTAL days off** (PTO + holidays + weekend) that a suggested period must include.                                                                  |
| `max_total_days_off`     | Integer          | `-1`    | The maximum number of **TOTAL days off** (PTO + holidays + weekend) that a suggested period can include. Use `-1` for no limit.                                            |
| `min_gap_days`           | Integer          | `0`     | The minimum number of days **between two vacation periods**.                                                                                                               |
| `top_n_suggestions`      | Integer          | `1`     | The number of **vacation suggestions**.                                                                                                                                    |
| `in_holiday_as_pto`      | Boolean          | `false` | If `true`, Fixed Days Off (holidays/weekends) inside a continuous vacation span are charged against the PTO budget. If `false`, only working days consume PTO.             |
| `custom_holidays`        | List of Strings  | `[]`    | List of additional non-working days. Supports single days ("YYYY-MM-DD") or ranges ("YYYY-MM-DD:YYYY-MM-DD").                                                              |
| `forced_work`            | List of Strings  | `[]`    | List of dates or intervals where work is mandatory. Supports single days ("YYYY-MM-DD") or ranges ("YYYY-MM-DD:YYYY-MM-DD").                                               |
| `must_be_vacation`       | List of Strings  | `[]`    | List of dates or intervals where vacation is mandatory (e.g., family trips or company shutdowns). Supports single days ("YYYY-MM-DD") or ranges ("YYYY-MM-DD:YYYY-MM-DD"). |
| `must_start_on`          | List of Strings  | `[]` | List of specific dates where a vacation period must begin. Each element anchors one of the suggested blocks to that exact date.                                            |
| `must_end_on`            | List of Strings  | `[]` | List of specific dates where a vacation period must end. Each element anchors one of the suggested blocks to that exact date.                                              |
| `required_months` | List of Integers | `[]` | List of months (1-12) where at least one vacation period must be entirely contained. The number of months selected cannot exceed max_periods.                              |

### ⚙️ `[ALGORITHM]`

This section configures the type of optimization algorithm and the specific scoring rule used to prioritize potential vacation breaks.

| Parameter | Type    | Default | Description                                                                                                                                                                                                                                                |
| :--- |:--------|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `algorithm_type` | `str` | `optimal` | `optimal`: Uses Dynamic Programming to find the mathematical global maximum. `greedy`: Selects best ROI first (Fast, heuristic-based).                                                                                                                     |
| `duration_weight_factor_alpha` | `float` | `0.5`      | The Alpha Factor ($\alpha$) that weights break duration. It calculates priority with the Score $P = \eta \times T^{\alpha}$. Values $\alpha > 0$ penalize short breaks and prioritize longer vacation periods ($T$). Use $0$ for Pure Efficiency ($\eta$). |

---

## 🌟 Support the project

If **Vacation Extender** was useful to you or helped you plan your vacations, please consider giving this repository a **star**!

This helps the project grow and motivates the creation of new smart solutions. 🚀

[Click here to give it a star!](https://github.com/afsmaira/vacationExtender/stargazers)