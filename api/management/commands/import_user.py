from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import csv
import os

class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def handle(self, *args, **options):
        csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../movielens_dataset'))
        csv_file_path = os.path.join(csv_dir, 'unique_user_ids.csv')
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                username = row['userId']
                password = row['Password']
                
                # Create user if it doesn't exist
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password=password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'User {username} created successfully'))
                else:
                    self.stdout.write(self.style.WARNING(f'User {username} already exists'))
