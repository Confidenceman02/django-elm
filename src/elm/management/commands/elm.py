from django.core.management.base import LabelCommand

from ...strategy import (
    AddProgramStrategy,
    CreateStrategy,
    InitStrategy,
    ListStrategy,
    NpmStrategy,
    Strategy,
)
from ...validate import Validations


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command arguments are missing, please add one of the following:
  create <app-name> - to create a djelm app
  init <app-name> - to initialize an Elm project in the <app-name> app
  addprogram <app-name> <program-name> - create an Elm program called <program-name> in the <app-name> app
  npm <app-name> [args].. - call your designated NODE_PACKAGE_MANAGER with [args]
  list - to list all your djelm apps
Usage example:
  python manage.py elm create djelm_app
  python manage.py elm init djelm_app
  python manage.py elm addprogram djelm_app MyElmProgram
  python manage.py elm npm djelm_app install
  python manage.py elm list
"""
    validate = None
    strategy: InitStrategy | CreateStrategy | AddProgramStrategy | ListStrategy | NpmStrategy

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    def handle(self, *labels, **options):
        return self.handle_labels(*labels)

    def handle_labels(self, *labels):
        self.strategy = Strategy().create(*labels)
        strat = self.run_strategy()

    def run_strategy(self):
        self.strategy.run(self.stdout, self.style)
        # if strat.tag == "Failure":
        #     raise strat.err
