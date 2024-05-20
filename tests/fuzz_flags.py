import random

from hypothesis import strategies as st
from djelm.flags.form.primitives import ModelChoiceFieldFlag

from djelm.flags.main import (
    BoolFlag,
    FloatFlag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
)

ALL_FLAGS = [
    ObjectFlag,
    ListFlag,
    NullableFlag,
    StringFlag,
    IntFlag,
    FloatFlag,
    BoolFlag,
    # TODO solve constructor name clashes
    # CustomTypeFlag,
    # forms
    ModelChoiceFieldFlag,
]


def generate_alias_keys() -> list[str]:
    keys = st.lists(
        # Added lookahead for reserved keywords
        st.from_regex(regex=r"^(?!\bif\W*$)[a-z][A-Za-z0-9_]*$"),
        min_size=1,
        max_size=5,
    ).example()
    return keys


def fuzz_flag():
    choice = random.choice(ALL_FLAGS)

    if choice is ObjectFlag:
        keys = generate_alias_keys()
        print(f"Generated these keys: {keys}")
        arg = {}

        for k in keys:
            k = k.replace("\n", "")
            arg[k] = fuzz_flag()

        return ObjectFlag(arg)
    if choice is ListFlag:
        return ListFlag(fuzz_flag())

    if choice is NullableFlag:
        return NullableFlag(fuzz_flag())

    # TODO solve constructor name clashes
    # if choice is CustomTypeFlag:
    #     variant_keys = generate_alias_keys()
    #     variants = []
    #
    #     for k in variant_keys:
    #         k = k.replace("\n", "")
    #         variants.append((k, fuzz_flag()))
    #
    #     return CustomTypeFlag(variants=variants)

    return choice()
