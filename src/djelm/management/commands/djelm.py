import argparse

from django.core.management.base import LabelCommand

from ...strategy import (
    AddProgramStrategy,
    CompileStrategy,
    CreateStrategy,
    ElmStrategy,
    GenerateModelStrategy,
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
  compile <app-name> - to compile all your elm programs in the given <app-name> app
  compilebuild <app-name> - to compile all your elm programs with a production level build in the given <app-name> app
Usage example:
  python manage.py djelm create djelm_app
  python manage.py djelm addprogram djelm_app MyElmProgram
  python manage.py djelm watch djelm_app
  python manage.py djelm npm djelm_app install
  python manage.py djelm elm djelm_app install <elm-package>
  python manage.py djelm generatemodel djelm_app MyElmProgram
  python manage.py djelm list
  python manage.py djelm compile djelm_app
  python manage.py djelm compilebuild djelm_app
"""
    validate = None
    strategy: CreateStrategy | AddProgramStrategy | ListStrategy | NpmStrategy | ElmStrategy | WatchStrategy | GenerateModelStrategy | CompileStrategy

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    def add_arguments(self, parser):
        _, unknown = parser.parse_known_args()

        if 1 < len(unknown) and unknown[1] in ["npm"]:
            parser.add_argument("strategy")
            parser.add_argument("app")
            parser.add_argument("rest", nargs=argparse.REMAINDER)

        else:
            super(Command, self).add_arguments(parser)

    def handle(self, *labels, **options):  # type:ignore
        if len(labels) == 0:
            # We are dealing with an npm strategy when there are no labels
            return self.handle_labels(
                *(options["strategy"], options["app"], *options["rest"])
            )
        return self.handle_labels(*labels, **options)

    def handle_labels(self, *labels, **options):
        self.strategy = Strategy().create(*labels)
        self.run_strategy()

    def run_strategy(self):
        self.strategy.run(self.stdout, self.style)
