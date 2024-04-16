from djelm.flags.form.helpers import ModelChoiceFieldVariant
from djelm.flags.main import Flags

from test_programs.models import Car


class TestModelChoiceFieldVariant:
    def test_field_objects_fields(self):
        SUT = ModelChoiceFieldVariant(Car)

        assert SUT.get_field_objects()["fields"] == ["manufacturer", "country"]

    def test_field_objects_flag_parser(self):
        flag = ModelChoiceFieldVariant(Car).get_field_objects()["flag"]
        SUT = Flags(flag)

        assert (
            SUT.parse({"manufacturer": "Mazda", "country": "Japan"})
            == '{"manufacturer":"Mazda","country":"Japan"}'
        )

    def test_get_classname(self):
        SUT = ModelChoiceFieldVariant(Car)

        assert SUT.get_classname() == "Car"

    def test_get_instance_values(self):
        SUT = ModelChoiceFieldVariant(Car)

        assert SUT.get_instance_values(Car(manufacturer="Mazda", country="Japan")) == {
            "manufacturer": "Mazda",
            "country": "Japan",
        }
