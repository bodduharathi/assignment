import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_monitoring.settings')
django.setup()
import csv
from datetime import datetime
from pytz import timezone as pytz_timezone
from django.utils import timezone as dj_timezone
from monitoring.models import StoreStatus, BusinessHours, StoreTimezone
from django.db.models import Max



def load_store_statuses(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse timestamp_utc string to datetime object
            timestamp_utc_str = row['timestamp_utc']
            timestamp_utc = datetime.strptime(timestamp_utc_str, '%Y-%m-%d %H:%M:%S.%f UTC')

            # Get store timezone from StoreTimezone model
            store_timezone = StoreTimezone.objects.filter(store_id=row['store_id']).first()
            if store_timezone:
                timezone_obj = pytz_timezone(store_timezone.timezone_str)
            else:
                timezone_obj = pytz_timezone('America/Chicago')  # Default timezone if not specified

            # Convert timestamp_utc to aware datetime in store timezone
            timestamp_aware = timezone_obj.localize(timestamp_utc)

            # Create StoreStatus object
            store_status = StoreStatus(
                store_id=row['store_id'],
                timestamp_utc=timestamp_aware,
                status=row['status']
            )
            store_status.save()


def load_business_hours(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Set default values for missing start_time_local and end_time_local
            start_time_local = row.get('start_time_local', '00:00:00')
            end_time_local = row.get('end_time_local', '23:59:59')

            # Create BusinessHours object
            business_hours = BusinessHours(
                store_id=row['store_id'],
                day_of_week=int(row['day']),
                start_time_local=start_time_local,
                end_time_local=end_time_local
            )
            business_hours.save()

def load_store_timezones(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Set default timezone to 'America/Chicago' if missing
            timezone_str = row.get('timezone_str', 'America/Chicago')

            # Create StoreTimezone object
            store_timezone = StoreTimezone(
                store_id=row['store_id'],
                timezone_str=timezone_str
            )
            store_timezone.save()

if __name__ == '__main__':
    # Set the Django settings module for the script
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_monitoring.settings')
    django.setup()

    # Path to the CSV files for each data source
    status_csv_path = 'store status.csv'
    business_hours_csv_path = 'Menu hours.csv'
    timezone_csv_path = 'bq-results-20230125-202210-1674678181880.csv'

    # Load data from CSV files into corresponding Django models
    load_store_statuses(status_csv_path)
    load_business_hours(business_hours_csv_path)
    load_store_timezones(timezone_csv_path)
