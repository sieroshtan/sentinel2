import datetime

from job import Job
from sandbox import Sandbox


def _parse_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').date()


def run(date_to, date_from=None):
    date_to = _parse_date(date_to)

    if date_from:
        date_from = _parse_date(date_from)
    else:
        date_from = date_to

    job = Job(Sandbox('temp'))

    if date_from <= date_to:
        job.run(date_from, date_to)
    else:
        print("start date > end date")
