from prefect.schedules import Interval
from orchestrate import scraping_flow
from datetime import timedelta, datetime

scraping_flow.serve(
    name = 'scraping',
    schedule = Interval(
        timedelta(hours = 24),
        anchor_date = datetime(2025, 1, 1, 0, 0),
        timezone = 'Brazil/Recife'
    )
)