from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StoreStatus, BusinessHours, StoreTimezone, GeneratedReport
from datetime import datetime, timedelta
from django.utils import timezone as dj_timezone
from django.db.models import Max
import csv
import uuid
import pytz
import io
import json

def interpolate_status_count(status_entries, start_time, end_time):
    """
    Interpolate or extrapolate status counts within a specified time interval.
    """
    total_duration = (end_time - start_time).total_seconds() / 60  # Total duration in minutes
    count = 0

    for entry in status_entries:
        entry_time = entry.timestamp_utc
        if start_time <= entry_time < end_time:
            count += 1

    if total_duration > 0:
        return (count / total_duration) * 60  # Convert to count per hour
    else:
        return 0


import pytz  # Add this import statement

def calculate_uptime_downtime(store_id, business_hours, current_time):
    """
    Calculate uptime and downtime within specified business hours for a given store.
    """
    uptime_last_hour = 0
    downtime_last_hour = 0
    uptime_last_day = 0
    downtime_last_day = 0
    uptime_last_week = 0
    downtime_last_week = 0

    for hours in business_hours:
        # Retrieve the store's timezone from StoreTimezone model
        store_timezone = StoreTimezone.objects.filter(store_id=store_id).first()
        if store_timezone:
            timezone_str = store_timezone.timezone_str
            timezone_obj = pytz.timezone(timezone_str)  # Use pytz.timezone to get the timezone object
        else:
            # Use a default timezone if store's timezone is not found
            timezone_obj = pytz.timezone('America/Chicago')  # Replace with your default timezone

        # Convert local start and end times to aware datetime objects in the store's timezone
        start_time_local = hours.start_time_local
        end_time_local = hours.end_time_local
        start_time_utc = timezone_obj.localize(datetime.combine(datetime.today(), start_time_local))
        end_time_utc = timezone_obj.localize(datetime.combine(datetime.today(), end_time_local))

        # Filter StoreStatus data within time range and last week
        status_entries = StoreStatus.objects.filter(
            store_id=store_id,
            timestamp_utc__gte=start_time_utc,
            timestamp_utc__lt=end_time_utc,
            timestamp_utc__lte=current_time - timedelta(days=7)  # Within the last week
        )

        # Calculate uptime and downtime for the last hour, day, and week
        if hours.day_of_week == current_time.weekday():
            # Calculate uptime and downtime for the last hour
            uptime_last_hour += interpolate_status_count(status_entries, current_time - timedelta(hours=1), current_time)
            downtime_last_hour = 60 - uptime_last_hour  # Total minutes in an hour

        # Calculate uptime and downtime for the last day and week
        uptime_last_day += interpolate_status_count(status_entries, current_time - timedelta(days=1), current_time)
        uptime_last_week += interpolate_status_count(status_entries, current_time - timedelta(days=7), current_time)

    downtime_last_day = 1440 - uptime_last_day  # Total minutes in a day (24 hours)
    downtime_last_week = (24 * 7 * 60) - uptime_last_week  # Total minutes in a week (7 days)

    return {
        'uptime_last_hour': round(uptime_last_hour, 2),
        'downtime_last_hour': round(downtime_last_hour, 2),
        'uptime_last_day': round(uptime_last_day / 60, 2),  # Convert minutes to hours
        'downtime_last_day': round(downtime_last_day / 60, 2),  # Convert minutes to hours
        'uptime_last_week': round(uptime_last_week / 60, 2),  # Convert minutes to hours
        'downtime_last_week': round(downtime_last_week / 60, 2),  # Convert minutes to hours
    }

@csrf_exempt
def trigger_report(request):
    """
    Endpoint to trigger report generation.
    """
    if request.method == 'POST':
        # Generate a unique report_id
        report_id = str(uuid.uuid4())

        # Create a new report entry in the database
        report = GeneratedReport.objects.create(report_id=report_id, status='Running')

        # Asynchronously start report generation (could be done in a background task)
        generate_report_data(report_id)

        return JsonResponse({'report_id': report_id})
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

import csv
from django.http import JsonResponse, HttpResponse
from .models import GeneratedReport

@csrf_exempt
def get_report(request):
    """
    Endpoint to get the report status or data.
    """
    if request.method == 'GET':
        report_id = request.GET.get('report_id')
        if not report_id:
            return JsonResponse({'error': 'Invalid report_id'}, status=400)

        try:
            report = GeneratedReport.objects.get(report_id=report_id)
            if report.status == 'Running':
                return JsonResponse({'status': 'Running'})

            elif report.status == 'Complete':
                # Generate CSV data based on the report data
                csv_data = generate_csv_data(report.data)

                # Prepare HTTP response with CSV attachment
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="report_{report_id}.csv"'

                # Write the CSV data to the response
                writer = csv.writer(response)
                csv_data_list = csv_data.split("\n")
                for row in csv_data_list:
                    writer.writerow(row.split(','))

                # Construct the JSON response
                json_response = {'status': 'Complete'}

                # Encode the JSON response into bytes
                json_response_bytes = json.dumps(json_response).encode('utf-8')

                # Attach the JSON response to the CSV response
                response.write('\n\n')  # Add a newline separator between CSV and JSON
                response.write(json_response_bytes)

                return response

        except GeneratedReport.DoesNotExist:
            return JsonResponse({'error': 'Report not found'}, status=404)

    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

def generate_csv_data(report_data):
    """
    Generate CSV data based on the report data.
    """
    # Extract the store_id and uptime/downtime data from the report data
    store_id = report_data.get('store_id', '')
    uptime_last_hour = report_data.get('uptime_last_hour', 0)
    downtime_last_hour = report_data.get('downtime_last_hour', 0)
    uptime_last_day = report_data.get('uptime_last_day', 0)
    downtime_last_day = report_data.get('downtime_last_day', 0)
    uptime_last_week = report_data.get('uptime_last_week', 0)
    downtime_last_week = report_data.get('downtime_last_week', 0)

    # Define the CSV data as a list of lists (rows)
    csv_data = [
        ['Store ID', 'Uptime Last Hour', 'Downtime Last Hour', 'Uptime Last Day', 'Downtime Last Day', 'Uptime Last Week', 'Downtime Last Week'],
        [store_id, uptime_last_hour, downtime_last_hour, uptime_last_day, downtime_last_day, uptime_last_week, downtime_last_week]
    ]

    # Create a CSV string using csv module
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)

    return output.getvalue()



def generate_report_data(report_id):
    """
    Function to generate report data asynchronously.
    """
    # Retrieve all stores
    stores = StoreTimezone.objects.all()

    for store in stores:
        store_id = store.store_id
        timezone_str = store.timezone_str

        # Get business hours for the store
        business_hours = BusinessHours.objects.filter(store_id=store_id)

        # Retrieve the maximum timestamp from StoreStatus data
        max_timestamp = StoreStatus.objects.aggregate(max_timestamp=Max('timestamp_utc'))['max_timestamp']
        current_time = dj_timezone.now() if max_timestamp is None else max_timestamp

        # Calculate uptime and downtime within business hours
        result = calculate_uptime_downtime(store_id, business_hours, current_time)

        # Store report data in the database
        report = GeneratedReport.objects.get(report_id=report_id)
        report.data = {
            'store_id': store_id,
            'uptime_last_hour': result['uptime_last_hour'],
            'downtime_last_hour': result['downtime_last_hour'],
            'uptime_last_day': result['uptime_last_day'],
            'downtime_last_day': result['downtime_last_day'],
            'uptime_last_week': result['uptime_last_week'],
            'downtime_last_week': result['downtime_last_week'],
        }
        report.status = 'Complete'
        report.save()
