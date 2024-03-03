import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Course


class Command(BaseCommand):
    help = "Loads course data from CSV file"

    def handle(self, *args, **options):
        datafile = settings.BASE_DIR / "core" / "data" / "courses.csv"

        with open(datafile) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Course.objects.get_or_create(name=row[0], instructor=row[1])
