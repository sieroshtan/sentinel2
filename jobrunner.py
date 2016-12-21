import datetime

from job import Job
from models import SentinelScene


def _get_existing_dates():
    return [scene.datetime.strftime('%Y-%m-%d') for scene in SentinelScene.select()]


def _get_next_date_from(existing_dates):
    return max(existing_dates) + datetime.timedelta(days=1)


def _parse_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').date()


def run(date_to, date_from=None):
    existing_dates = _get_existing_dates()

    if date_from:
        date_from = _parse_date(date_from)
    elif existing_dates:
        date_from = _get_next_date_from(existing_dates)
    else:
        raise ValueError("Cannot determine start date. Please specify explicitly.")

    date_to = _parse_date(date_to)

    job = Job()

    if date_from <= date_to:
        job.run(date_from, date_to)
    elif date_to not in existing_dates:
        job.run(date_to, date_to)
    else:
        print("Scene already processed in DB")
