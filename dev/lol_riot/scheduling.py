import time
from apscheduler.schedulers.background import BackgroundScheduler
from data_population_script import main as populate_data
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def start_scheduler():
    """Starts the scheduler for periodic data updates."""
    scheduler = BackgroundScheduler()
    update_interval = int(
        os.getenv("DATA_UPDATE_INTERVAL", 3600)
    )  # Default to 1 hour if not specified

    # Add job for data population
    scheduler.add_job(
        populate_data, "interval", seconds=update_interval, id="data_population_job"
    )

    try:
        scheduler.start()
        print(f"Scheduling data population every {update_interval} seconds.")
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
