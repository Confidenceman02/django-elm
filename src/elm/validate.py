import subprocess


class ValidationError(Exception):
    pass


class Validations:
    @staticmethod
    def acceptable_label(label) -> bool:
        if label not in [
            "init"
        ]:
            raise ValidationError(f"Subcommand '{label}' doesn't exist")
        return True

    @staticmethod
    def has_elm_binary() -> bool:
        try:
            subprocess.check_output(["which", "elm"])
        except subprocess.CalledProcessError as err:
            raise ValidationError(
                'I can"t find an "elm" binary.\n Go to https://guide.elm-lang.org/install/elm.html for instructions '
                f'on how to install elm.\n {err}'
            )

        return True
