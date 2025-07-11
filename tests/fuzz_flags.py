import random

from hypothesis import strategies as st
from djelm.flags.form.primitives import (
    ModelChoiceFieldFlag,
    ModelMultipleChoiceFieldFlag,
)

from djelm.flags.main import (
    BoolFlag,
    FloatFlag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
)
from djelm.flags.primitives import AliasFlag

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
    ModelMultipleChoiceFieldFlag,
]


def generate_alias_keys() -> list[str]:
    keys = st.lists(
        # Added lookahead for reserved keywords
        st.from_regex(regex=r"^(?!\b(if|in)\W*$)[a-z][A-Za-z0-9_]*$"),
        min_size=1,
        max_size=5,
    ).example()
    return keys


def generate_alias_names() -> list[str]:
    keys = st.lists(
        # Added lookahead for reserved keywords
        st.from_regex(regex=r"^[A-Z][A-Za-z0-9_]*$"),
        min_size=1,
        max_size=5,
        unique=True,
    ).example()
    return keys


def fuzz_alias_flags() -> list[AliasFlag]:
    names = generate_alias_names()
    result = []
    keys = generate_alias_keys()

    for name in names:
        name = name.replace("\n", "")
        obj = {}

        for key in keys:
            obj[key] = StringFlag()
        result.append(AliasFlag(name, ObjectFlag(obj)))

    return result


ALL_ALIAS_FLAGS = fuzz_alias_flags()


def fuzz_flag():
    choice = random.choice([*ALL_FLAGS, ALL_ALIAS_FLAGS])

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

    if isinstance(choice, list):
        return random.choice(choice)

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
