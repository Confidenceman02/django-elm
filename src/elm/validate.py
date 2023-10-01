import os.path
import subprocess
from typing_extensions import TypedDict
from typing import Literal

from .effect import ExitSuccess, ExitFailure

Init = TypedDict(
    "Init", {'command': Literal["init"], 'app_name': str})
Create = TypedDict(
    "Create", {'command': Literal["create"], 'app_name': str})
List = TypedDict(
    "List", {'command': Literal["list"]})
InitValidation = TypedDict(
    'InitValidation',
    {'value': Init})


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(self, labels: list[str]) -> (
            ExitSuccess[Init | Create] |
            ExitFailure[list[str], ValidationError]
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
                if os.path.isdir(os.path.join(os.getcwd(), app_name)):
                    raise ValidationError(
                        f"It looks like you are trying to run the 'create' command on the {app_name} app.\n"
                        f"I can't 'create' an app that has already been created.\n"
                        f"Perhaps you meant to run the 'init' command?")

    def __check_command_combos(self, xs: list[str]) -> None:
        match xs:
            case ["init", _]:
                return
            case ["create", _]:
                return
            case ["list", _]:
                raise ValidationError("The 'list' command doesn't take any arguments\nTry - python manage.py elm list")
            case ["list"]:
                return
            case ["init"] as command_verb:
                raise ValidationError(self.__missing_app_log(command_verb[0]))
            case ["create"] as command_verb:
                raise ValidationError(self.__missing_app_log(command_verb[0]))

    @staticmethod
    def has_elm_binary() -> ExitSuccess[None] | ExitFailure:
        try:
            subprocess.check_output(["which", "elm"])
            return ExitSuccess(None)
        except subprocess.CalledProcessError as err:
            return ExitFailure[None, ValidationError](
                None,
                ValidationError(
                    'I can"t find an "elm" binary.\n Go to https://guide.elm-lang.org/install/elm.html for instructions'
                    f'on how to install elm.\n {err}'
                ))

    @staticmethod
    def __missing_app_log(cmd_verb: str) -> str:
        return f"""
        Missing argument:
        
        The '{cmd_verb}' command is expecting an <app-name>"
        
        "The <app-name>  lets me know what app you want me to '{cmd_verb}'."
        """

    @staticmethod
    def __check_command_verb(s: str) -> None:
        if s not in ["init", "create", "list"]:
            raise ValidationError(f"The command '{s}' is not valid.")

    @staticmethod
    def __command_exit(xs: list[str]) -> (
            ExitSuccess[Init | Create | List] |
            ExitFailure[list[str], ValidationError]
    ):
        match xs:
            case ["init", v]:
                arg: Init = {'command': 'init', 'app_name': v}
                return ExitSuccess(arg)
            case ["create", v]:
                return ExitSuccess({'command': 'create', 'app_name': v})
            case ["list"]:
                return ExitSuccess({'command': 'list'})
            case _ as cmds:
                return ExitFailure(cmds, ValidationError(
                    f"\nI can't handle the command arguments {str(cmds)}"))
