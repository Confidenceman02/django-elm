module {{cookiecutter.program_name}} exposing (..)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)
import Json.Decode exposing (decodeValue)
import Json.Encode exposing (Value)
import Models.{{cookiecutter.program_name}} exposing (ToModel, toModel)


type Msg
    = Increment
    | Decrement


type Model
    = Ready ToModel
    | Error


init : Value -> ( Model, Cmd Msg )
init f =
    case decodeValue toModel f of
        Ok m ->
            ( Ready m, Cmd.none )

        Err _ ->
            ( Error, Cmd.none )


main : Program Value Model Msg
main =
    Browser.element
        { init = init
        , update = update
        , view = view
        , subscriptions = subscriptions
        }


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case model of
        Ready m ->
            case msg of
                Increment ->
                    ( Ready (m + 1), Cmd.none )

                Decrement ->
                    ( Ready (m - 1), Cmd.none )

        _ ->
            ( model, Cmd.none )


view : Model -> Html Msg
view model =
    case model of
        Ready m ->
            div []
                [ button [ onClick Decrement ] [ text "-" ]
                , div [] [ text (String.fromInt m) ]
                , button [ onClick Increment ] [ text "+" ]
                ]

        _ ->
            text ""
