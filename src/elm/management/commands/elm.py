from django.core.management.base import LabelCommand

from ...strategy import (
    AddProgramStrategy,
    CreateStrategy,
    InitStrategy,
    ListStrategy,
    Strategy,
)
from ...validate import Validations


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command arguments are missing, please add one of the following:
  create <app-name> - to create a django-elm app
  init <app-name> - to initialize a current django-elm app
  list - to list all your djelm projects
  addprogram <app-name> <program-name> - creates a boilerplate for a djelm program
Usage example:
  python manage.py elm create <app-name>
  python manage.py elm init <app-name>
  python manage.py elm list
  python manage.py elm addprogram <app-name> <program-name>
    """
    validate = None
    strategy: InitStrategy | CreateStrategy | AddProgramStrategy | ListStrategy

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
