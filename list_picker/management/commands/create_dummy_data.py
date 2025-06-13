from django.core.management.base import BaseCommand
from faker import Faker
from list_picker.models import Team, Employee

class Command(BaseCommand):
    help = 'Create dummy data for teams and employees'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(10):
            team = Team.objects.create(name=fake.company())
            for _ in range(10):
                Employee.objects.create(name=fake.name(), team=team)
        self.stdout.write(self.style.SUCCESS('Successfully created 10 teams with 10 employees each'))