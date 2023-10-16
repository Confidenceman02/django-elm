from typing import Literal

from django.core.management import settings
from typing_extensions import TypedDict

from .effect import ExitFailure, ExitSuccess
from .utils import get_app_path, is_create, is_djelm, is_init, walk_level

Init = TypedDict("Init", {"command": Literal["init"], "app_name": str})
Create = TypedDict("Create", {"command": Literal["create"], "app_name": str})
List = TypedDict("List", {"command": Literal["list"]})
AddProgram = TypedDict(
    "AddProgram",
    {"command": Literal["addprogram"], "app_name": str, "program_name": str},
)
InitValidation = TypedDict("InitValidation", {"value": Init})
Npm = TypedDict(
    "Npm",
    {"command": Literal["npm"], "app_name": str, "args": list[str]},
)


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(
        self, labels: list[str], *args
    ) -> (
        ExitSuccess[Init | Create | List | AddProgram | Npm]
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
                        f"""
It looks like you are trying to run the 'create' command on the {app_name} app.

I can't 'create' an app that has already been created.

Perhaps you meant to run the 'init' command?

To see all the available commans run:
python manage.py elm

"""
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
                if is_init(app_name):
                    raise ValidationError(
                        f"\nI can't run 'init' on the {app_name} app because it looks like you already have am elm.json file."
                    )
            case ["npm", app_name, *rest]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("npm", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(self.__not_a_django_app_log("npm"))
            case ["addprogram", _]:
                raise ValidationError(
                    """
                    Missing a program name:\n
                    To set up an elm program I need a name.\n
                    Try running something like: 'python manage.py elm addprogram <program>'
                    """
                )

            case ["addprogram", app_name, _]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("addprogram", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{self.__not_a_django_app_log("addprogram")}\n'
                        f"make sure the "
                    )
                if not is_init(app_name) or not is_create(app_name):
                    raise ValidationError(
                        f"It looks like you are missing some files/directories.\n"
                        f"In order form me to add a program I need to see the following files/directories:\n"
                        f"{app_name}/elm.json, {app_name}/src/, {app_name}/templates/, {app_name}/templatetags/\n"
                        f"Make sure you have run both 'python manage.py elm create {app_name}' and 'python manage.py elm init {app_name}' before adding a program"
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
            case [
                "npm",
                _,
            ]:
                raise ValidationError(
                    "I was expecting some arguments for the 'npm' command. run 'python manage.py elm to see examples.'\n"
                )
            case [
                "npm",
            ]:
                raise ValidationError(self.__missing_app_log("npm"))
            case ["npm", _, *rest]:
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

It looks like you are trying to run the '{cmd_verb}' command on a djelm app that is not listed in your settings.py.

Make sure that '{app_name}' exists in your INSTALLED_APPS in settings.py or try run 'python manage.py elm create {app_name}' to create the app if you haven't already.

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
        if s not in ["init", "create", "npm", "list", "addprogram"]:
            raise ValidationError(f"The command '{s}' is not valid.")

    @staticmethod
    def __command_exit(
        xs: list[str],
    ) -> (
        ExitSuccess[Init | Create | List | AddProgram | Npm]
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
            case ["npm", v, *rest]:
                return ExitSuccess({"command": "npm", "app_name": v, "args": rest})
            case ["list"]:
                return ExitSuccess({"command": "list"})
            case _ as cmds:
                return ExitFailure(
                    cmds,
                    ValidationError(
                        f"\nI can't handle the command arguments {str(cmds)}"
                    ),
                )
