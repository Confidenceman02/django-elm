module Main exposing (..)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)


main : Program () Int Msg
main =
    Browser.element
        { init = always ( 0, Cmd.none )
        , update = update
        , view = view
        , subscriptions = subscriptions
        }


type Msg
    = Increment
    | Decrement


subscriptions : Int -> Sub Msg
subscriptions _ =
    Sub.none


update : Msg -> Int -> ( Int, Cmd Msg )
update msg model =
    case msg of
        Increment ->
            ( model + 1, Cmd.none )

        Decrement ->
            ( model - 1, Cmd.none )


view : Int -> Html Msg
view model =
    div []
        [ button [ onClick Decrement ] [ text "-" ]
        , div [] [ text (String.fromInt model) ]
        , button [ onClick Increment ] [ text "+" ]
        ]
