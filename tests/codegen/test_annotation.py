import djelm.codegen.annotation as Anno


class TestToString:
    def test_with_string(self):
        anno = Anno.string()
        SUT = Anno.toString(anno)

        assert SUT == "String"

    def test_with_int(self):
        anno = Anno.int()
        SUT = Anno.toString(anno)

        assert SUT == "Int"

    def test_with_float(self):
        anno = Anno.float()
        SUT = Anno.toString(anno)

        assert SUT == "Float"

    def test_with_bool(self):
        anno = Anno.bool()
        SUT = Anno.toString(anno)

        assert SUT == "Bool"

    def test_with_maybe_string(self):
        anno = Anno.maybe(Anno.string())
        SUT = Anno.toString(anno)

        assert SUT == "Maybe String"

    def test_with_maybe_int(self):
        anno = Anno.maybe(Anno.int())
        SUT = Anno.toString(anno)

        assert SUT == "Maybe Int"

    def test_with_maybe_float(self):
        anno = Anno.maybe(Anno.float())
        SUT = Anno.toString(anno)

        assert SUT == "Maybe Float"

    def test_with_maybe_bool(self):
        anno = Anno.maybe(Anno.bool())
        SUT = Anno.toString(anno)

        assert SUT == "Maybe Bool"

    def test_with_maybe_list_string(self):
        anno = Anno.maybe(Anno.list(Anno.string()))
        SUT = Anno.toString(anno)

        assert SUT == "Maybe (List String)"

    def test_with_list_string(self):
        anno = Anno.list(Anno.string())
        SUT = Anno.toString(anno)

        assert SUT == "List String"

    def test_with_alias(self):
        anno = Anno.alias("Something", Anno.string())
        SUT = Anno.toString(anno)

        assert SUT == "Something"

    def test_with_record_fields(self):
        anno = Anno.record([("hello", Anno.string()), ("world", Anno.string())])
        SUT = Anno.toString(anno)

        assert (
            SUT
            == """{ hello : String
, world : String
}"""
        )

    def test_with_record_field(self):
        anno = Anno.record([("hello", Anno.string())])
        SUT = Anno.toString(anno)

        assert SUT == """{ hello : String }"""
