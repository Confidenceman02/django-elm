import subprocess
from typing_extensions import TypedDict
from typing import Literal

Value = TypedDict(
    "Value", {'command': Literal["init"] | Literal["create"], 'app_name': str})
ExitSuccess = TypedDict(
    'ExitSuccess',
    {'_tag': Literal["Success"],
     'value': Value})

ExitFailure = TypedDict("ExitFailure", {'_tag': Literal["Failure"]})

Exit = ExitSuccess | ExitFailure


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(self, labels: list[str]) -> Exit:
        try:
            self.__check_command_verb(labels[0])
            self.__check_command_combos(labels)
            return self.__command_exit(labels)
        except Exception as err:
            raise err

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
    def has_elm_binary() -> None:
        try:
            subprocess.check_output(["which", "elm"])
        except subprocess.CalledProcessError as err:
            raise ValidationError(
                'I can"t find an "elm" binary.\n Go to https://guide.elm-lang.org/install/elm.html for instructions '
                f'on how to install elm.\n {err}'
            )

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
    def __command_exit(xs: list[str]) -> ExitSuccess:
        match xs:
            case ["init", v]:
                return {
                    '_tag': 'Success',
                    'value': {'command': 'init', 'app_name': v}
                }
            case ["create", v]:
                return {
                    '_tag': 'Success',
                    'value': {'command': 'create', 'app_name': v}
                }

            case _ as cmds:
                raise ValidationError(f"Im not able to handle these commands {cmds}")
