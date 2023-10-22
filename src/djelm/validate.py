from typing import Literal

from django.core.management import settings
from typing_extensions import TypedDict

from .effect import ExitFailure, ExitSuccess
from .utils import get_app_path, is_create, is_djelm, is_init, is_program, walk_level

Create = TypedDict("Create", {"command": Literal["create"], "app_name": str})
List = TypedDict("List", {"command": Literal["list"]})
AddProgram = TypedDict(
    "AddProgram",
    {"command": Literal["addprogram"], "app_name": str, "program_name": str},
)
Npm = TypedDict(
    "Npm",
    {"command": Literal["npm"], "app_name": str, "args": list[str]},
)
Elm = TypedDict(
    "Elm",
    {"command": Literal["elm"], "app_name": str, "args": list[str]},
)
Watch = TypedDict(
    "Watch",
    {"command": Literal["watch"], "app_name": str},
)
GenerateModel = TypedDict(
    "GenerateModel",
    {"command": Literal["generatemodel"], "app_name": str, "program_name": str},
)


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(
        self, labels: list[str], *args
    ) -> (
        ExitSuccess[Create | List | AddProgram | Npm | Elm | Watch | GenerateModel]
        | ExitFailure[list[str], ValidationError]
    ):
        try:
            self.__check_command_verb(labels[0])
            self.__check_command_combos(labels)
            self.__check_existing(labels)
            return self.__command_exit(labels)
        except ValidationError as err:
            return ExitFailure(labels, err)

    def __check_existing(self, xs: list[str]) -> None:
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

To see all the available commans run:
manage.py djelm

"""
                    )

                if app_name in settings.INSTALLED_APPS:
                    raise ValidationError(
                        f"{self.__not_a_django_app_log('create')}\n"
                        f"Make sure the <app-name> does not already exist."
                    )
            case ["npm", app_name, *rest]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("npm", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(self.__not_a_django_app_log("npm"))
            case ["elm", app_name, *rest]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("elm", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(self.__not_a_django_app_log("elm"))
            case ["watch", app_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("watch", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(f'{self.__not_a_django_app_log("watch")}\n')
            case ["addprogram", _]:
                raise ValidationError(
                    """
                    Missing a program name:\n
                    To set up an elm program I need a name.\n
                    Try running something like: 'manage.py djelm addprogram <program>'
                    """
                )

            case ["generatemodel", _]:
                raise ValidationError(
                    """
                    Missing a program name:\n
                    I need to know what program to generate a model for.\n
                    Try running something like: 'manage.py djelm generatemodel <program>'
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
                        f"Make sure you have run 'manage.py djelm create {app_name}' before adding a program"
                    )

            case ["generatemodel", app_name, p]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("generatemodel", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{self.__not_a_django_app_log("generatemodel")}\n'
                        f"make sure the "
                    )
                if (
                    not is_init(app_name)
                    or not is_create(app_name)
                    or not is_program(app_name, p)
                ):
                    raise ValidationError(
                        f"It looks like you are missing some files/directories that I was expecting to be present.\n"
                        f"In order for me to generate a model I need to see the following files/directories:\n"
                        f"{app_name}/static_src/elm.json, {app_name}/templates/, {app_name}/templatetags/ {app_name}/static_src/src/{p}.elm\n"
                        f"Make sure you have run 'manage.py djelm create {app_name}' and 'manage.py djelm addprogram {p}' as those commands will generate everything I need to generating a model."
                    )

    def __check_command_combos(self, xs: list[str]) -> None:
        match xs:
            case ["create", _]:
                return
            case ["watch", _]:
                return
            case ["addprogram", _, _]:
                return
            case ["generatemodel", _, _]:
                return
            case ["list", _]:
                raise ValidationError(
                    "The 'list' command doesn't take any arguments\nTry - manage.py djelm list"
                )
            case ["list"]:
                return
            case [
                "npm",
                _,
            ]:
                raise ValidationError(
                    "I was expecting some arguments for the 'npm' command. run 'manage.py djelm to see examples.'\n"
                )
            case [
                "elm",
                _,
            ]:
                raise ValidationError(
                    "I was expecting some arguments for the 'elm' command. run 'manage.py djelm to see examples.'\n"
                )
            case [
                "npm",
            ]:
                raise ValidationError(self.__missing_app_name_log("npm"))
            case [
                "elm",
            ]:
                raise ValidationError(self.__missing_app_name_log("elm"))
            case ["npm", _, *_]:
                return
            case ["elm", _, *_]:
                return
            case ["watch"] as command_verb:
                raise ValidationError(self.__missing_app_name_log(command_verb[0]))

            case ["create"] as command_verb:
                raise ValidationError(self.__missing_app_name_log(command_verb[0]))

    @staticmethod
    def __missing_app_name_log(cmd_verb: str) -> str:
        return f"""
        Missing argument:
        
        The '{cmd_verb}' command is expecting an <app-name>"
        
        "The <app-name>  lets me know what app you want me to '{cmd_verb}'."
        """

    @staticmethod
    def __not_in_settings(cmd_verb: str, app_name: str) -> str:
        return f"""

It looks like you are trying to run the '{cmd_verb}' command on a djelm app that is not listed in your settings.py.

Make sure that '{app_name}' exists in your INSTALLED_APPS in settings.py or try run 'manage.py djelm create {app_name}' to create the app if you haven't already.

"""

    @staticmethod
    def __not_a_django_app_log(cmd_verb: str) -> str:
        return f"""
        f"It looks like you are trying to run the '{cmd_verb}' command on an installed app that was not "
        f"created by djelm.\n"
        f"I can't run {cmd_verb} on external apps that already exist.\n"
        """

    @staticmethod
    def __check_command_verb(s: str) -> None:
        if s not in [
            "create",
            "npm",
            "elm",
            "list",
            "addprogram",
            "watch",
            "generatemodel",
        ]:
            raise ValidationError(f"The command '{s}' is not valid.")

    @staticmethod
    def __command_exit(
        xs: list[str],
    ) -> (
        ExitSuccess[Create | List | AddProgram | Npm | Elm | Watch | GenerateModel]
        | ExitFailure[list[str], ValidationError]
    ):
        match xs:
            case ["create", v]:
                return ExitSuccess({"command": "create", "app_name": v})
            case ["watch", v]:
                return ExitSuccess({"command": "watch", "app_name": v})
            case ["addprogram", v, p]:
                return ExitSuccess(
                    {"command": "addprogram", "app_name": v, "program_name": p}
                )
            case ["generatemodel", v, p]:
                return ExitSuccess(
                    {"command": "generatemodel", "app_name": v, "program_name": p}
                )
            case ["npm", v, *rest]:
                return ExitSuccess({"command": "npm", "app_name": v, "args": rest})
            case ["elm", v, *rest]:
                return ExitSuccess({"command": "elm", "app_name": v, "args": rest})
            case ["list"]:
                return ExitSuccess({"command": "list"})
            case _ as cmds:
                return ExitFailure(
                    cmds,
                    ValidationError(f"\nI can't handle the command arguments {cmds!s}"),
                )
