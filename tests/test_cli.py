import os
from django.core.management import call_command


# import pytest

# from src.elm.validate import ValidationError


def test_elm_init(settings):
    call_command("elm", "nonsense")
    assert os.path.isfile(os.path.join("elm_project", "apps.py")), 'The Elm app has been generated'
