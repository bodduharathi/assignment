from django.db import models

class StoreStatus(models.Model):
    store_id = models.IntegerField()
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)  # Assuming 'status' can be 'active' or 'inactive'

    def __str__(self):
        return f"Store {self.store_id} - {self.status} at {self.timestamp_utc}"


class BusinessHours(models.Model):
    store_id = models.IntegerField()
    day_of_week = models.IntegerField()  # 0=Monday, 6=Sunday
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    def __str__(self):
        return f"Business hours for Store {self.store_id} on day {self.day_of_week}"


class StoreTimezone(models.Model):
    store_id = models.IntegerField()
    timezone_str = models.CharField(max_length=50)  # e.g., 'America/Chicago'

    def __str__(self):
        return f"Timezone for Store {self.store_id}: {self.timezone_str}"
    
class GeneratedReport(models.Model):
    report_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, default='Running')
    data = models.JSONField(null=True)

    def __str__(self):
        return f"Report {self.report_id}"
