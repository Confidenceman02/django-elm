from django.core.management.base import LabelCommand

from ...validate import Validations
from ...elm import Elm
from ...strategy import Strategy, InitStrategy, CreateStrategy


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command argument is missing, please add one of the following:
  create <project-name> - to create a django-elm project
  init <project-name> - to initialize a current django-elm project
Usage example:
  python manage.py elm create
    """
    validate = None
    elm: type(Elm) | None = None
    strategy: InitStrategy | CreateStrategy

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    def handle(self, *labels, **options):
        return self.handle_labels(*labels)

    def handle_labels(self, *labels):
        self.strategy = Strategy().create(*labels)
        self.handle_strategy()

    def handle_strategy(self):
        self.strategy.run(self.stdout, self.style)
