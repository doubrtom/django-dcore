from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


DAYS_IN_YEAR = Decimal('365.242199')
MONTHS_IN_YEAR = Decimal(12)


def parse_date(date_string: str) -> date:
    """Return date from date_string in format 'YYYY-MM-DD'."""
    return datetime.strptime(date_string, '%Y-%m-%d').date()


def get_age(date_instance: date) -> tuple:
    """Return age from birth date.

    Returns:
        tuple: Age in format of tuple (years, months, days)
    """
    now_date = datetime.now().date()
    age_diff = relativedelta(now_date, date_instance)
    return age_diff.years, age_diff.months, age_diff.days


def date_diff(date_from: date, date_to: date) -> tuple:
    """Return difference between two days.

    Returns:
        tuple: Difference in format of tuple (years, moths, days)
    """
    age_diff = relativedelta(date_to, date_from)
    return age_diff.years, age_diff.months, age_diff.days


def days_months_years_to_years(days: int, months: int, years: int) -> Decimal:
    """Return age (days + months + years) converted to decimal number representing years.

    For number of days/months in years see DAYS_IN_YEAR and MONTHS_IN_YEAR constants in this module.
    """
    return (Decimal(days) / DAYS_IN_YEAR) + (Decimal(months) / MONTHS_IN_YEAR) + Decimal(years)
