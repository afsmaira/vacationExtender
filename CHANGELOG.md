# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-05-21

### Added
- **Required Months:** New constraint to ensure at least one full vacation period is contained within specific months (useful for school holidays or seasonal planning).
- **UI Translation:** Added localized month names for both English and Portuguese.

## [0.2.0] - 2024-05-21

### Added
- **Anchor Constraints:** New `must_start_on` and `must_end_on` parameters to force vacation periods to align with specific dates (e.g., booked flights).
- **Mandatory Vacation Days:** Added `must_be_vacation` parameter to ensure specific dates are included in the generated plans.
- **UI Updates:** New advanced settings section in the Streamlit app with multi-language support (EN/PT).

## [0.1.1] - 2024-05-19
### Fixed
- Minor bug fixes in holiday calculation.

## [0.1.0] - 2024-05-18
### Added
- Initial release of VacationExtender.