class ValidationError(Exception):
    pass


class Validations:
    def acceptable_label(self, label):
        if label not in [
            "init"
        ]:
            raise ValidationError(f"Subcommand '{label}' doesn't exist")
