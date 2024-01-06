module Main2 exposing (..)

import Browser
import Html exposing (Html, div, text)
import Json.Decode exposing (decodeValue)
import Json.Encode exposing (Value)
import Models.Main2 exposing (ToModel, toModel)


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
update _ model =
    ( model, Cmd.none )


view : Model -> Html Msg
view model =
    case model of
        Ready _ ->
            div []
                [ text "Main2 test"
                ]

        _ ->
            text ""
