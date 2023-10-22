from django.core.management.base import LabelCommand

from ...strategy import (
    AddProgramStrategy,
    CreateStrategy,
    ElmStrategy,
    ListStrategy,
    NpmStrategy,
    Strategy,
    WatchStrategy,
)
from ...validate import Validations


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command arguments are missing, please add one of the following:
  create <app-name> - to create a djelm app
  addprogram <app-name> <program-name> - create an Elm program called <program-name> in the <app-name> app
  watch <app-name> - will watch the app's src file for Elm code changes and compile
  npm <app-name> [args].. - call your designated NODE_PACKAGE_MANAGER with [args]
  elm <app-name> [args].. - call your designated ELM_BIN_PATH with [args]
  generatemodel <app-name> [args].. - generate a model for the existing program <program-name> in the <app-name> app
  list - to list all your djelm apps
Usage example:
  python manage.py djelm create djelm_app
  python manage.py djelm addprogram djelm_app MyElmProgram
  python manage.py djelm watch djelm_app
  python manage.py djelm npm djelm_app install
  python manage.py djelm elm djelm_app install <elm-package>
  python manage.py djelm generatemodel djelm_app MyElmProgram
  python manage.py djelm list
"""
    validate = None
    strategy: CreateStrategy | AddProgramStrategy | ListStrategy | NpmStrategy | ElmStrategy | WatchStrategy

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
