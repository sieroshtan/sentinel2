import datetime

from job import Job
from sandbox import Sandbox


def _parse_date(date_str):
    """
    Convert date string to datetime object
    :param date_str:
    :return:
    """
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def run(farm_id, date_to, date_from=None):
    """
    Check input params. Parse dates. Run main parsing job.
    :param farm_id:
    :param date_to:
    :param date_from:
    :return:
    """
    date_to = _parse_date(date_to)

    if date_from:
        date_from = _parse_date(date_from)
    else:
        date_from = date_to

    job = Job(farm_id, Sandbox('temp'))

    if date_from <= date_to:
        job.run(date_from, date_to)
    else:
        print("start date > end date")
