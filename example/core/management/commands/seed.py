import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Course, Extra


class Command(BaseCommand):
    help = "Loads course data from CSV file"

    def handle(self, *args, **options):
        datafile_courses = settings.BASE_DIR / "core" / "data" / "courses.csv"
        datafile_extras = settings.BASE_DIR / "core" / "data" / "extras.csv"

        with open(datafile_courses) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Course.objects.get_or_create(name=row[0], instructor=row[1])
        with open(datafile_extras) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Extra.objects.get_or_create(name=row[0])
