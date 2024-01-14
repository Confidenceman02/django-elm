import typing
from dataclasses import dataclass

from pydantic import BaseModel, Field, Strict, TypeAdapter, validate_call
from typing_extensions import Annotated

_annotated_string = Annotated[str, Strict()]
_annotated_int = Annotated[int, Strict()]
_annotated_float = Annotated[float, Strict()]
_annotated_bool = Annotated[bool, Strict()]
_annotated_alias_key = Annotated[str, Field(pattern=r"^[a-z][A-Za-z0-9_]*$")]

_StringAdapter = TypeAdapter(_annotated_string)
_IntAdapter = TypeAdapter(_annotated_int)
_FloatAdapter = TypeAdapter(_annotated_float)
_BoolAdapter = TypeAdapter(_annotated_bool)

PreparedElm = typing.TypedDict("PreparedElm", {"alias_type": str, "decoder_body": str})


@validate_call
def valid_alias_key(k: _annotated_alias_key):
    return k


@dataclass(slots=True)
class StringDecoder:
    """Decoder helper for the Elm String primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {StringDecoder._raw_decoder()}"""

    def alias(self) -> str:
        return f"""{self.value} : {StringDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {StringDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.string"

    @staticmethod
    def _raw_type():
        return "String"


@dataclass(slots=True)
class IntDecoder:
    """Decoder helper for the Elm Int primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {IntDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {IntDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {IntDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.int"

    @staticmethod
    def _raw_type():
        return "Int"


@dataclass(slots=True)
class BoolDecoder:
    """Decoder helper for the Elm Bool primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {BoolDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {BoolDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {BoolDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.bool"

    @staticmethod
    def _raw_type():
        return "Bool"


@dataclass(slots=True)
class FloatDecoder:
    """Decoder helper for the Elm Float primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {FloatDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {FloatDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {FloatDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.float"

    @staticmethod
    def _raw_type():
        return "Float"


@dataclass(slots=True)
class ListDecoder:
    """Decoder helper for the Elm List primitive"""

    value: str
    targetDecoderName: str
    targetTypeName: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {ListDecoder._raw_decoder(self.targetDecoderName)}"""

    def alias(self):
        return f"""{self.value} : {self._raw_type(self.targetTypeName)}"""

    def nested_alias(self):
        return f""", {self.value} : List {self.targetTypeName}"""

    @staticmethod
    def _raw_decoder(decoder_def: str):
        return f"(Decode.list {decoder_def})"

    @staticmethod
    def _raw_type(targetType: str):
        return f"(List {targetType})"


@dataclass(slots=True)
class NullableDecoder:
    """Decoder helper for the Elm Maybe monad"""

    value: str
    targetDecoderName: str
    targetTypeName: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {NullableDecoder._raw_decoder(self.targetDecoderName)}"""

    def alias(self):
        return f"""{self.value} : Maybe {self.targetTypeName}"""

    def nested_alias(self):
        return f""", {self.value} : Maybe {self.targetTypeName}"""

    @staticmethod
    def _raw_decoder(decoder_def: str):
        return f"(Decode.nullable {decoder_def})"

    @staticmethod
    def _raw_type(targetType: str):
        return f"(Maybe {targetType})"


@dataclass(slots=True)
class ObjectDecoder:
    """Decoder helper for the Elm {} primitive"""

    value: str
    depth: int

    def pipeline(self):
        return f"""|>  required "{self.value}" {self._to_decoder_name()}"""

    def pipeline_starter(self):
        return f"""{self._to_decoder_annotation()}\n    {self._to_pipeline_succeed()}"""

    def alias(self):
        return f"""{self.value} : {self._to_alias()}"""

    def nested_alias(self):
        return f""", {self.value} : {self._to_alias()}"""

    def _to_alias(self) -> str:
        return self.value[0].upper() + self.value[1:] + self._depth_markers()

    def _to_decoder_annotation(self):
        return f"""{self.value + self._depth_markers()}Decoder : Decode.Decoder {self._to_alias()}\n{self._to_decoder_name()} ="""

    def _to_decoder_name(self):
        return f"""{self.value + self._depth_markers()}Decoder"""

    def _to_alias_definition(self, body: str):
        return f"""\n\ntype alias {self._to_alias()} =\n    {body}"""

    def _to_pipeline_succeed(self):
        return f"""Decode.succeed {self._to_alias()}"""

    def _depth_markers(self) -> str:
        marker = ""
        for _ in range(self.depth):
            marker += "_"
        return marker


@dataclass(slots=True)
class StringFlag:
    """Flag for the Elm String primitive"""


@dataclass(slots=True)
class IntFlag:
    """Flag for the Elm Int primitive"""


@dataclass(slots=True)
class FloatFlag:
    """Flag for the Elm Float primitive"""


@dataclass(slots=True)
class BoolFlag:
    """Flag for the Elm Bool primitive"""


@dataclass(slots=True)
class NullableFlag:
    """Flag for the Elm Maybe monad"""

    obj: "Primitive"


@dataclass(slots=True)
class ListFlag:
    """Flag for the Elm List primitive"""

    obj: "Primitive"


@dataclass(slots=True)
class ObjectFlag:
    """Flag for the Elm {} primitive"""

    obj: typing.Dict[str, "Primitive"]


Primitive = (
    StringFlag | IntFlag | FloatFlag | BoolFlag | ListFlag | ObjectFlag | NullableFlag
)
FlagsObject = dict[str, "PrimitiveFlag"]
FlagsList = list["PrimitiveFlag"]
FlagsNullable = typing.Union[type[str], type[int], type[float], type[bool], type[None]]
PrimitiveObjectFlagType = (
    type[str]
    | type[int]
    | type[float]
    | type[bool]
    | type[BaseModel]
    | type[list]
    | FlagsNullable
)
PrimitiveFlag = (
    str | int | float | bool | FlagsObject | FlagsList | FlagsNullable | None
)
ObjHelperReturn = typing.TypedDict(
    "ObjHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": typing.Dict[str, PrimitiveObjectFlagType],
        "elm_values": PreparedElm,
        "alias_extra": str,
        "decoder_extra": str,
    },
)
SingleHelperReturn = typing.TypedDict(
    "SingleHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": PrimitiveObjectFlagType,
        "elm_values": PreparedElm,
        "alias_extra": str,
        "decoder_extra": str,
    },
)


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, d):
        prepared_flags = (
            _prepare_pipeline_flags(d, "Decode.succeed ToModel")
            if isinstance(d, ObjectFlag)
            else _prepare_inline_flags(d, ObjectDecoder("inlineToModel", 1))
        )

        class Prepared:
            """Validator and Elm values builder"""

            @staticmethod
            def parse(input) -> str:
                prepared_flags["adapter"].validate_python(input)
                return prepared_flags["adapter"].dump_json(input).decode("utf-8")

            @staticmethod
            def to_elm_parser_data() -> PreparedElm:
                if isinstance(d, ObjectFlag):
                    return prepared_flags["elm_values"]
                else:
                    return {
                        "alias_type": prepared_flags["elm_values"]["alias_type"]
                        + prepared_flags["alias_extra"],
                        "decoder_body": prepared_flags["elm_values"]["decoder_body"]
                        + prepared_flags["decoder_extra"],
                    }

        return Prepared


def _prepare_inline_flags(
    d: Primitive, object_decoder: ObjectDecoder | None = None, depth: int = 1
) -> SingleHelperReturn:
    adapter: TypeAdapter
    anno: PrimitiveObjectFlagType
    alias_type: str = ""
    decoder_body = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    match d:
        case StringFlag():
            adapter = _StringAdapter
            anno = _annotated_string
            alias_type = StringDecoder._raw_type()
            decoder_body = StringDecoder._raw_decoder()
        case IntFlag():
            adapter = _IntAdapter
            anno = _annotated_int
            alias_type = IntDecoder._raw_type()
            decoder_body = IntDecoder._raw_decoder()
        case FloatFlag():
            adapter = _FloatAdapter
            anno = _annotated_float
            alias_type = FloatDecoder._raw_type()
            decoder_body = FloatDecoder._raw_decoder()
        case BoolFlag():
            adapter = _BoolAdapter
            anno = _annotated_bool
            alias_type = BoolDecoder._raw_type()
            decoder_body = BoolDecoder._raw_decoder()
        case NullableFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[typing.Optional[t], None])
            anno = typing.Optional[t]  # type:ignore
            alias_type = NullableDecoder._raw_type(
                single_flag["elm_values"]["alias_type"]
            )
            alias_extra += single_flag["alias_extra"]
            decoder_body = NullableDecoder._raw_decoder(
                single_flag["elm_values"]["decoder_body"]
            )
            decoder_extra += single_flag["decoder_extra"]
        case ListFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[list[t], None])
            anno = list[t]  # type:ignore
            alias_type = ListDecoder._raw_type(single_flag["elm_values"]["alias_type"])
            alias_extra += single_flag["alias_extra"]
            decoder_body = ListDecoder._raw_decoder(
                single_flag["elm_values"]["decoder_body"]
            )
            decoder_extra += single_flag["decoder_extra"]
        case ObjectFlag(obj=obj):
            if object_decoder is None:
                raise Exception(f"Missing an ObjectDecoder argument for {obj}")
            object_flag = _prepare_pipeline_flags(
                d, object_decoder.pipeline_starter(), depth + 1
            )
            t = object_flag["anno"]  # type:ignore

            adapter = object_flag["adapter"]
            anno = t  # type:ignore
            alias_type = object_decoder._to_alias()
            alias_extra = object_decoder._to_alias_definition(
                object_flag["elm_values"]["alias_type"]
            )
            decoder_body = object_decoder._to_decoder_name()
            decoder_extra = f"\n\n{object_flag['elm_values']['decoder_body']}"
        case _:
            raise Exception(f"Can't resolve core_schema type for: {d}")
    return {
        "adapter": adapter,
        "anno": anno,
        "elm_values": {
            "alias_type": alias_type,
            "decoder_body": decoder_body,
        },
        "alias_extra": alias_extra,
        "decoder_extra": decoder_extra,
    }


def _prepare_pipeline_flags(
    d: ObjectFlag, decoder_start: str, depth: int = 1
) -> ObjHelperReturn:
    anno: typing.Dict[str, PrimitiveObjectFlagType] = {}
    pipeline_decoder: str = decoder_start
    alias_values: str = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    for idx, (k, v) in enumerate(d.obj.items()):
        try:
            k = k.replace("\n", "")
            valid_alias_key(k)
            match v:
                case ObjectFlag(obj=obj):
                    prepared_object_recursive = _prepare_pipeline_flags(
                        ObjectFlag(obj),
                        ObjectDecoder(k, depth).pipeline_starter(),
                        depth + 1,
                    )
                    anno[k] = type(
                        "K",
                        (BaseModel,),
                        {
                            "__annotations__": prepared_object_recursive[
                                "anno"
                            ].__origin__.__annotations__  # type:ignore
                        },
                    )

                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['elm_values']['decoder_body']}"
                    )
                    alias_extra += ObjectDecoder(k, depth)._to_alias_definition(
                        prepared_object_recursive["elm_values"]["alias_type"]
                    )
                    pipeline_decoder += (
                        f"""\n        {ObjectDecoder(k, depth).pipeline()}"""
                    )
                    if idx == 0:
                        alias_values += f" {ObjectDecoder(k, depth).alias()}"
                    else:
                        alias_values += (
                            f"\n    {ObjectDecoder(k, depth).nested_alias()}"
                        )

                case ListFlag(obj=obj):
                    single_flag = _prepare_inline_flags(obj, ObjectDecoder(k, depth))
                    list_decoder = ListDecoder(
                        k,
                        single_flag["elm_values"]["decoder_body"],
                        single_flag["elm_values"]["alias_type"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = list[single_flag["anno"]]  # type:ignore

                    pipeline_decoder += f"""\n        {list_decoder.pipeline()}"""

                    if idx == 0:
                        alias_values += f" {list_decoder.alias()}"
                    else:
                        alias_values += f"\n    {list_decoder.nested_alias()}"
                case NullableFlag(obj=obj1):
                    single_flag = _prepare_inline_flags(obj1, ObjectDecoder(k, depth))
                    nullable_decoder = NullableDecoder(
                        k,
                        single_flag["elm_values"]["decoder_body"],
                        single_flag["elm_values"]["alias_type"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = typing.Optional[single_flag["anno"]]  # type:ignore

                    pipeline_decoder += f"""\n        {nullable_decoder.pipeline()}"""

                    if idx == 0:
                        alias_values += f" {nullable_decoder.alias()}"
                    else:
                        alias_values += f"\n    {nullable_decoder.nested_alias()}"
                case StringFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {StringDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {StringDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {StringDecoder(k).nested_alias()}"

                case IntFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {IntDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {IntDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {IntDecoder(k).nested_alias()}"

                case FloatFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {FloatDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {FloatDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {FloatDecoder(k).nested_alias()}"

                case BoolFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {BoolDecoder(k).pipeline()}"""
                    if idx == 0:
                        alias_values += f" {BoolDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {BoolDecoder(k).nested_alias()}"

                case _:
                    raise Exception("Unsopported type")
        except Exception as err:
            raise err
    return {
        "adapter": TypeAdapter(
            Annotated[type("K", (BaseModel,), {"__annotations__": anno}), None]
        ),
        "anno": Annotated[  # type:ignore
            type("K", (BaseModel,), {"__annotations__": anno}), None
        ],
        "elm_values": {
            "alias_type": "{" + alias_values + "\n    }" + alias_extra,
            "decoder_body": pipeline_decoder + decoder_extra,
        },
        "alias_extra": alias_extra,
        "decoder_extra": decoder_extra,
    }


class Flags(BaseFlag):
    """
    A class for validating djelm flags that are used in Elm programs.

    f1 = Flags(ObjectFlag({"hello": StringFlag}))
    f1.parse({"hello": "world"}) -> '{"hello":"world"}'

    f2 = Flags(StringFlag())
    f2.parse("hello world") -> '"hello world"'
    """

    if typing.TYPE_CHECKING:
        parse: typing.Callable[[PrimitiveFlag], str]
        to_elm_parser_data: typing.Callable[[], dict[str, str]]
