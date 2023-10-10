from typing import Literal

from django.core.management import settings
from typing_extensions import TypedDict

from .effect import ExitFailure, ExitSuccess
from .utils import get_app_path, is_djelm, is_init, walk_level

Init = TypedDict("Init", {"command": Literal["init"], "app_name": str})
Create = TypedDict("Create", {"command": Literal["create"], "app_name": str})
List = TypedDict("List", {"command": Literal["list"]})
AddProgram = TypedDict(
    "AddProgram",
    {"command": Literal["addprogram"], "app_name": str, "program_name": str},
)
InitValidation = TypedDict("InitValidation", {"value": Init})


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(
        self, labels: list[str]
    ) -> (
        ExitSuccess[Init | Create | List | AddProgram]
        | ExitFailure[list[str], ValidationError]
    ):
        try:
            self.__check_command_verb(labels[0])
            self.__check_command_combos(labels)
            self.__check_existing_app(labels)
            return self.__command_exit(labels)
        except ValidationError as err:
            return ExitFailure(labels, err)

    def __check_existing_app(self, xs: list[str]) -> None:
        match xs:
            case ["create", app_name]:
                app_path_exit = get_app_path(app_name)

                if app_path_exit.tag == "Success" and is_djelm(
                    next(walk_level(app_path_exit.value))[2]
                ):
                    raise ValidationError(
                        f"It looks like you are trying to run the 'create' command on the {app_name} app.\n"
                        f"I can't 'create' an app that has already been created.\n"
                        f"Perhaps you meant to run the 'init' command?"
                    )

                if app_name in settings.INSTALLED_APPS:
                    raise ValidationError(
                        f"{self.__not_a_django_app_log('create')}\n"
                        f"Make sure the <app-name> does not already exist."
                    )
            case ["init", app_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("init", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{self.__not_a_django_app_log("init")}\n' f"make sure the "
                    )
            case ["addprogram", app_name]:
                raise ValidationError(
                    """
                    Missing a program name:\n
                    To set up an elm program I need a name.\n
                    Try running something like: 'python manage.py elm addprogram <program>'
                    """
                )

            case ["addprogram", app_name, prog_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("addprogram", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{self.__not_a_django_app_log("init")}\n' f"make sure the "
                    )
                if not is_init(app_name):
                    raise ValidationError(
                        f"I can't find an 'elm.json' file or 'src' directory.\n"
                        f"Make sure you run 'python manage.py elm init {app_name} before adding a program'"
                    )

    def __check_command_combos(self, xs: list[str]) -> None:
        match xs:
            case ["init", _]:
                return
            case ["create", _]:
                return
            case ["addprogram", _, _]:
                return
            case ["list", _]:
                raise ValidationError(
                    "The 'list' command doesn't take any arguments\nTry - python manage.py elm list"
                )
            case ["list"]:
                return
            case ["init"] as command_verb:
                raise ValidationError(self.__missing_app_log(command_verb[0]))
            case ["create"] as command_verb:
                raise ValidationError(self.__missing_app_log(command_verb[0]))

    @staticmethod
    def __missing_app_log(cmd_verb: str) -> str:
        return f"""
        Missing argument:
        
        The '{cmd_verb}' command is expecting an <app-name>"
        
        "The <app-name>  lets me know what app you want me to '{cmd_verb}'."
        """

    @staticmethod
    def __not_in_settings(cmd_verb: str, app_name: str) -> str:
        return f"""
        f"It looks like you are trying to run the '{cmd_verb}' command on an app that is not installed in "
        f"your settings.py.\n"
        f"Make sure that {app_name} exists in your INSTALLED_APPS in settings.py or try run 'python "
        f"manage.py"
        f"create {app_name}' to create the app.\n"
        """

    @staticmethod
    def __not_a_django_app_log(cmd_verb: str) -> str:
        return f"""
        f"It looks like you are trying to run the '{cmd_verb}' command on an installed app that was not "
        f"created by django-elm.\n"
        f"I can't run {cmd_verb} on external apps that already exist.\n"
        """

    @staticmethod
    def __check_command_verb(s: str) -> None:
        if s not in ["init", "create", "list", "addprogram"]:
            raise ValidationError(f"The command '{s}' is not valid.")

    @staticmethod
    def __command_exit(
        xs: list[str],
    ) -> (
        ExitSuccess[Init | Create | List | AddProgram]
        | ExitFailure[list[str], ValidationError]
    ):
        match xs:
            case ["init", v]:
                arg: Init = {"command": "init", "app_name": v}
                return ExitSuccess(arg)
            case ["create", v]:
                return ExitSuccess({"command": "create", "app_name": v})
            case ["addprogram", v, p]:
                return ExitSuccess(
                    {"command": "addprogram", "app_name": v, "program_name": p}
                )
            case ["list"]:
                return ExitSuccess({"command": "list"})
            case _ as cmds:
                return ExitFailure(
                    cmds,
                    ValidationError(
                        f"\nI can't handle the command arguments {str(cmds)}"
                    ),
                )
