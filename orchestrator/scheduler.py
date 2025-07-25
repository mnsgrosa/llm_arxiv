from prefect.schedules import Interval
from orchestrator.orchestrate import scraping_flow
from datetime import timedelta, datetime

def main():
    scraping_flow.serve(
        name = 'scraping',
        schedule = Interval(
            timedelta(hours = 24),
            anchor_date = datetime(2025, 1, 1, 0, 0),
            timezone = 'America/New_York'
        )
    )

if __name__ == '__main__':
    main()