from typing import Literal

from django.conf import settings
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
Compile = TypedDict(
    "Compile",
    {"command": Literal["compile"], "app_name": str, "build": bool},
)


class ValidationError(Exception):
    pass


class Validations:
    def acceptable_command(
        self, labels: list[str], *_
    ) -> (
        ExitSuccess[
            Create | List | AddProgram | Npm | Elm | Watch | GenerateModel | Compile
        ]
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
\033[91m-- APP ALREADY EXISTS ------------------------------------------------------------------------------------------------------------------------- command/create\033[0m

It looks like you are trying to run the command: 

    \033[93mcreate\033[0m

The app you are targeting is:

    \033[93m{app_name}\033[0m 

But according to your \033[1mINSTALLED_APPS\033[0m variable \033[1m{app_name}\033[0m already exists and I can't \033[1m'create'\033[0m an app that has already been created."""
                    )

                if app_name in settings.INSTALLED_APPS:
                    raise ValidationError(
                        Validations.__not_a_djelm_app("create", app_name)
                    )
            case ["npm", app_name, *_]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        Validations.__not_in_settings("npm", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        Validations.__not_a_djelm_app("npm", app_name)
                    )
            case ["elm", app_name, *_]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        Validations.__not_in_settings("elm", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        Validations.__not_a_djelm_app("elm", app_name)
                    )
            case ["watch", app_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("watch", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{Validations.__not_a_djelm_app("watch", app_name)}\n'
                    )
            case ["compile", app_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(self.__not_in_settings("compile", app_name))
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{Validations.__not_a_djelm_app("compile", app_name)}\n'
                    )
            case ["compilebuild", app_name]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("compilebuild", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{Validations.__not_a_djelm_app("compilebuild", app_name)}\n'
                    )
            case ["addprogram", app_name]:
                raise ValidationError(
                    f"""

{Validations.__missing_program_name("addprogram", app_name)}

\033[4m\033[1mHint\033[0m: It helps if the name you choose describes what the program will do, something like \033[1mAddressPicker\033[0m or \033[1mImageCarousel\033[0m.

            e.g. \033[93mdjelm addprogram {app_name} ImageCarousel\033[0m"""
                )

            case ["generatemodel", app_name]:
                raise ValidationError(
                    f"""
{Validations.__missing_program_name("generatemodel", app_name)}"""
                )

            case ["addprogram", app_name, _]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("addprogram", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        f'{Validations.__not_a_djelm_app("addprogram", app_name)}\n'
                    )
                if not is_init(app_name) or not is_create(app_name):
                    raise ValidationError(
                        f"""
                        {Validations.__missing_files_directories(
                            "addprogram",
                            app_name,
                            [
                                f"{app_name}/static_src/elm.json",
                                f"{app_name}/templates/",
                                f"{app_name}/templatetags/",
                            ],
                        )}
\033[4m\033[1mHint\033[0m: These files are usually automatically generated for you when you run the \033[1mcreate\033[0m commands."""
                    )

            case ["generatemodel", app_name, p]:
                app_path_exit = get_app_path(app_name)

                if not app_path_exit.tag == "Success":
                    raise ValidationError(
                        self.__not_in_settings("generatemodel", app_name)
                    )
                if not is_djelm(next(walk_level(app_path_exit.value))[2]):
                    raise ValidationError(
                        Validations.__not_a_djelm_app("generatemodel", app_name)
                    )
                if (
                    not is_init(app_name)
                    or not is_create(app_name)
                    or not is_program(app_name, p)
                ):
                    raise ValidationError(
                        f"""
                        {Validations.__missing_files_directories(
                            "generatemodel",
                            app_name,
                            [
                                f"{app_name}/static_src/elm.json",
                                f"{app_name}/templates/",
                                f"{app_name}/templatetags/",
                                f"{app_name}/static_src/src/{p}.elm",
                            ],
                        )}
\033[4m\033[1mHint\033[0m: These files are usually automatically generated for you when you run the \033[1mcreate\033[0m and \033[1maddprogram\033[0m commands."""
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
            case ["list"]:
                return
            case ["compile", _]:
                return
            case ["compilebuild", _]:
                return
            case ["list", *rest]:
                raise ValidationError(
                    Validations.__too_many_command_args("list", list(rest))
                )
            case [
                "npm",
            ]:
                raise ValidationError(Validations.__missing_app_name("npm"))
            case [
                "compile",
            ]:
                raise ValidationError(Validations.__missing_app_name("compile"))
            case [
                "compilebuild",
            ]:
                raise ValidationError(Validations.__missing_app_name("compilebuild"))
            case ["compile", app_name, *rest]:
                raise ValidationError(
                    Validations.__too_many_command_args(
                        "compile " + app_name, list(rest)
                    )
                )
            case ["compilebuild", app_name, *rest]:
                raise ValidationError(
                    Validations.__too_many_command_args(
                        "compilebuild " + app_name, list(rest)
                    )
                )
            case [
                "elm",
            ]:
                raise ValidationError(Validations.__missing_app_name("elm"))
            case ["npm", _, *_]:
                return
            case ["elm", _, *_]:
                return
            case ["watch"] as command_verb:
                raise ValidationError(Validations.__missing_app_name(command_verb[0]))

            case ["create"] as command_verb:
                raise ValidationError(Validations.__missing_app_name(command_verb[0]))

    @staticmethod
    def __too_many_command_args(cmd_verb: str, args: list[str]) -> str:
        extra_args = ""
        for arg in args:
            extra_args += f"{arg} "
        return f"""

\033[91m-- TOO MANY ARGUMENTS ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

You also included these arguments:

    \033[93m{extra_args}\033[0m

But the \033[1m{cmd_verb}\033[0m command doesn't take any extra arguments.

\033[4m\033[1mHint\033[0m: Try just running \033[1mpython manage.py djelm {cmd_verb}\033[0m"""

    @staticmethod
    def __missing_files_directories(
        cmd_verb: str, app_name: str, files: list[str]
    ) -> str:
        missing = ""

        for file in files:
            missing += f"{file}\n    "
        return f"""
\033[91m-- MISSING FILES/DIRECTORIES ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

The app you are targeting is:

    \033[93m{app_name}\033[0m

But the {cmd_verb} command needs these files/directories to be present:

    \033[93m{missing}\033[0m"""

    @staticmethod
    def __missing_program_name(cmd_verb: str, app_name: str) -> str:
        return f"""
\033[91m-- MISSING PROGRAM NAME ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

The app you are targeting is:

    \033[93m{app_name}\033[0m

But you haven't included the name of the Elm program you want me to run this command against.
Make sure that you include a program name when running the \033[1m{cmd_verb}\033[0m command."""

    @staticmethod
    def __missing_app_name(cmd_verb: str) -> str:
        return f"""

\033[91m-- MISSING APP NAME ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m
        
It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

But you haven't included the name of the djelm app you want me to run this command against.

\033[4m\033[1mHint\033[0m: You can list your current djelm apps by running:

        \033[93mmanage.py djelm list\033[0m"""

    @staticmethod
    def __invalid_strategy(cmd_verb: str) -> str:
        return f"""

\033[91m-- INVALID STRATEGY ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

But I don't recognise that command.

Perhaps you meant one of these?:

        \033[93mcreate
        addprogram
        watch
        npm
        elm
        generatemodel
        list\033[0m"""

    @staticmethod
    def __not_in_settings(cmd_verb: str, app_name: str) -> str:
        return f"""

\033[91m-- MISSING APP ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

The app you are targeting is:

    \033[93m{app_name}\033[0m

But I cant find the \033[1m{app_name}\033[0m app.

\033[4m\033[1mHint\033[0m: Make sure that \033[1m{app_name}\033[0m exists in your \033[1mINSTALLED_APPS\033[0m variable in \033[1msettings.py\033[0m"""

    @staticmethod
    def __not_a_djelm_app(cmd_verb: str, app_name: str) -> str:
        return f"""

\033[91m-- NOT A DJELM APP ------------------------------------------------------------------------------------------------------------------------- command/{cmd_verb}\033[0m

It looks like you are trying to run the command:

    \033[93m{cmd_verb}\033[0m

The app you are targeting is:

    \033[93m{app_name}\033[0m

But \033[1m{app_name}\033[0m doesn't look like a djelm app and I can't run commands on apps I didn't create."""

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
            "compile",
            "compilebuild",
        ]:
            raise ValidationError(Validations.__invalid_strategy(s))

    @staticmethod
    def __command_exit(
        xs: list[str],
    ) -> (
        ExitSuccess[
            Create | List | AddProgram | Npm | Elm | Watch | GenerateModel | Compile
        ]
        | ExitFailure[list[str], ValidationError]
    ):
        match xs:
            case ["create", v]:
                return ExitSuccess({"command": "create", "app_name": v})
            case ["watch", v]:
                return ExitSuccess({"command": "watch", "app_name": v})
            case ["compile", v]:
                return ExitSuccess(
                    {"command": "compile", "app_name": v, "build": False}
                )
            case ["compilebuild", v]:
                return ExitSuccess({"command": "compile", "app_name": v, "build": True})
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


# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKCYAN = '\033[96m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#
