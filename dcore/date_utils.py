from datetime import datetime, date
from dateutil.relativedelta import relativedelta


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
