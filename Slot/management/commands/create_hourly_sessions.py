# your_app/management/commands/create_hourly_sessions.py
from django.core.management.base import BaseCommand
from datetime import time, timedelta, datetime
from Slot.models import SwimmingSession

class Command(BaseCommand):
    help = 'Create hourly swimming sessions with a 20-person capacity and set price per person'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating hourly swimming sessions...'))

        start_of_day = time(6, 0)
        end_of_day = time(21, 0)
        current_time = start_of_day

        while current_time < end_of_day:
            end_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()

            # Create the session
            session = SwimmingSession.objects.create(
                start_time=current_time,
                end_time=end_time,
                capacity=20,
                price_per_person=200.00
            )
            session.save()
            self.stdout.write(self.style.SUCCESS(f"Session from {current_time} to {end_time} created."))

            # Move to the next hour
            current_time = end_time

        self.stdout.write(self.style.SUCCESS('All hourly sessions created successfully.'))
