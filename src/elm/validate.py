import subprocess
from typing_extensions import TypedDict
from typing import Literal

from .effect import ExitSuccess, ExitFailure

Init = TypedDict(
    "Init", {'command': Literal["init"], 'app_name': str})
Create = TypedDict(
    "Create", {'command': Literal["create"], 'app_name': str})
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
            return self.__command_exit(labels)
        except ValidationError as err:
            return ExitFailure(labels, err)

    def __check_command_combos(self, xs: list[str]) -> None:
        match xs:
            case ["init", _]:
                return
            case ["create", _]:
                return
            case ["init"] as command_verb:
                raise ValidationError(self.__missing_project_log(command_verb[0]))
            case ["create"] as command_verb:
                raise ValidationError(self.__missing_project_log(command_verb[0]))

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
    def __missing_project_log(cmd_verb: str) -> str:
        return f"""
        Missing argument:
        
        The '{cmd_verb}' command is expecting a <project-name>"
        
        "The <project-name>  lets me know what project you want me to '{cmd_verb}'."
        """

    @staticmethod
    def __check_command_verb(s: str) -> None:
        if s not in ["init", "create"]:
            raise ValidationError(f"The command '{s}' is not valid.")

    @staticmethod
    def __command_exit(xs: list[str]) -> (
            ExitSuccess[Init | Create] |
            ExitFailure[list[str], ValidationError]
    ):
        match xs:
            case ["init", v]:
                arg: Init = {'command': 'init', 'app_name': v}
                return ExitSuccess(arg)
            case ["create", v]:
                return ExitSuccess({'command': 'create', 'app_name': v})

            case _ as cmds:
                return ExitFailure(cmds, ValidationError(
                    f"\nI can't handle the command {str(cmds)}"))
