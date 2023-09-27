from django.core.management.base import CommandError, LabelCommand

from ...validate import ValidationError, Validations


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command argument is missing, please add one of the following:
  init - to initialize django-tailwind app
Usage example:
  python manage.py elm init
    """
    validate = None

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    def handle(self, *labels, **options):
        return self.handle_labels(*labels, **options)

    def handle_labels(self, *labels, **options):
        self.validate.acceptable_label(labels[0])
