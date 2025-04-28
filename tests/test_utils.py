from djelm.utils import is_elm_entrypoint


def test_valid_is_elm_entrypoint():
    content = """
module Main exposing (main)

main : Program JD.Value Model Msg
main =
    Browser.element
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }
    """
    assert is_elm_entrypoint(content)


def test_invalid_is_elm_entrypoint():
    content = """
module Main exposing (update)

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
    (model, Cmd.none)
    """
    assert is_elm_entrypoint(content) is False
