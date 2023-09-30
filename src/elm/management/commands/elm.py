import os
from django.core.management.base import CommandError, LabelCommand

from ...validate import Validations
from ...utils import install_pip_package, get_app_src_path
from ...elm import Elm
from elm import get_config


class Command(LabelCommand):
    help = "Runs elm commands"
    missing_args_message = """
Command argument is missing, please add one of the following:
  init - to initialize django-elm app
Usage example:
  python manage.py elm init
    """
    validate = None
    elm: type(Elm) | None = None

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.validate = Validations()

    # def add_arguments(self, parser):
    #     super(Command, self).add_arguments(parser)
    #     parser.add_argument(
    #         "--app-name",
    #         help="Sets the default app name on the elm project"
    #     )

    def handle(self, *labels, **options):
        return self.handle_labels(*labels, **options)

    def handle_labels(self, *labels, **options):
        self.validate.acceptable_command(list(*labels))
        self.elm = Elm(target_dir=get_app_src_path(*labels[1]))
        getattr(self, "handle_init_commands")(*labels[1:], **options)

    def handle_init_commands(self, **options):
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            self.stdout.write("Couldn't find cookie cutter, installing...")
            install_pip_package("cookiecutter")
            from cookiecutter.main import cookiecutter
        try:
            app_path = cookiecutter(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                output_dir=os.getcwd(),
                directory="project_template",
                no_input=True,
                overwrite_if_exists=False,
                extra_context={"app_name": options["app_name"].strip() if options.get("app_name") else "elm_framework"},
            )

            app_name = os.path.basename(app_path)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Elm project '{app_name}' "
                    f"has been successfully created. "
                    f"Please add '{app_name}' to INSTALLED_APPS in settings.py, "
                    f"then run the following command to install all packages "
                    f"dependencies: `python manage.py elm install`"
                )
            )

        except Exception as err:
            raise CommandError(err)
