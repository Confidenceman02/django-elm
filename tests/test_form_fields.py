import pytest
from django import forms

from djelm.flags.form.primitives import ModelChoiceFieldFlag
from test_programs.models import Car, Enthusiast


@pytest.fixture()
def basic_form():
    class UserForm(forms.ModelForm):
        car = forms.ModelChoiceField(
            queryset=Car.objects.all(),
            help_text="Do I detect.. Elm?",
        )

        class Meta:
            model = Enthusiast
            fields = ("username",)

    return UserForm


@pytest.mark.django_db
def test_model_choice_field_adapter(basic_form):
    car1 = Car(manufacturer="Mazda", country="Japan")
    car1.save()

    prepare_form = basic_form()

    try:
        ModelChoiceFieldFlag().adapter().validate_python(prepare_form["car"])
    except Exception:
        pytest.fail("Bound ModelChoiceField should not raise an error")

    assert True

    # Unbound form
    try:
        ModelChoiceFieldFlag().adapter().validate_python(basic_form)
    except Exception:
        assert True

    # Bound form
    try:
        ModelChoiceFieldFlag().adapter().validate_python(basic_form())
    except Exception:
        assert True
        return
    pytest.fail("Passing wrong shape should fail validation")


@pytest.mark.django_db
def test_model_choice_field_json_dump(basic_form):
    prepare_form = basic_form()
    adapter = ModelChoiceFieldFlag().adapter()

    validated = adapter.validate_python(prepare_form["car"])
    SUT = adapter.dump_json(validated).decode("utf-8")

    assert (
        SUT
        == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}'
    )


# TEST FLAGS
