from django.core.management.base import LabelCommand

from ...validate import Validations
from ...strategy import Strategy, InitStrategy, CreateStrategy


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command arguments are missing, please add one of the following:
  create <app-name> - to create a django-elm app
  init <app-name> - to initialize a current django-elm app
Usage example:
  python manage.py elm create <app-name>
  python manage.py elm init <app-name>
    """
    validate = None
    strategy: InitStrategy | CreateStrategy

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    def handle(self, *labels, **options):
        return self.handle_labels(*labels)

    def handle_labels(self, *labels):
        self.strategy = Strategy().create(*labels)
        self.run_strategy()

    def run_strategy(self):
        self.strategy.run(self.stdout, self.style)
