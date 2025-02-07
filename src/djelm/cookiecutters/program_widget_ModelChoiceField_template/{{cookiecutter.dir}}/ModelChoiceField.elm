module Widgets.ModelChoiceField exposing (..)

import Browser
import Css
import Html.Styled as Styled exposing (Html, text)
import Json.Decode exposing (decodeValue)
import Json.Encode exposing (Value)
import List.Extra
import Select exposing (MenuItem, initState, staticSelectIdentifier, update)
import Select.Styles as Styles
import Widgets.Models.ModelChoiceField exposing (Options_, ToModel, toModel)


{-| A djelm widget for the ModelChoiceField Django form field

This widget was generated and tested against the <https://package.elm-lang.org/packages/Confidenceman02/elm-select/10.4.4/> Elm package.

-}
type Msg
    = SelectMsg (Select.Msg Options_)


type alias ReadyModel =
    { selectState : Select.State
    , items : List (MenuItem Options_)
    , selectedItem : Maybe Options_
    , toModel : ToModel
    }


type Model
    = Ready ReadyModel
    | Error


toMenuItem : Options_ -> MenuItem Options_
toMenuItem option =
    Select.basicMenuItem { item = option, label = option.choice_label }
        |> Select.valueMenuItem option.value


toReadyModel : ToModel -> ReadyModel
toReadyModel m =
    { selectState = initState (staticSelectIdentifier m.auto_id)
    , items =
        List.map
            toMenuItem
            m.options
    , selectedItem = List.Extra.find (\opt -> opt.selected) m.options
    , toModel = m
    }


init : Value -> ( Model, Cmd Msg )
init f =
    case decodeValue toModel f |> Result.map toReadyModel of
        Ok m ->
            ( Ready m, Cmd.none )

        Err _ ->
            ( Error, Cmd.none )


main : Program Value Model Msg
main =
    Browser.element
        { init = init
        , view = view >> Styled.toUnstyled
        , update = update
        , subscriptions = \_ -> Sub.none
        }


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case model of
        Ready readyModel ->
            case msg of
                SelectMsg selectMsg ->
                    let
                        ( maybeAction, selectState, cmds ) =
                            Select.update selectMsg readyModel.selectState

                        updatedSelectedItem =
                            case maybeAction of
                                Just (Select.Select i) ->
                                    Just i

                                Just Select.Clear ->
                                    Nothing

                                _ ->
                                    readyModel.selectedItem
                    in
                    ( Ready
                        { readyModel
                            | selectState = selectState
                            , selectedItem = updatedSelectedItem
                        }
                    , Cmd.map SelectMsg cmds
                    )

        _ ->
            ( model, Cmd.none )


view : Model -> Html Msg
view model =
    case model of
        Ready readyModel ->
            let
                selected =
                    case readyModel.selectedItem of
                        Just opt ->
                            Just (toMenuItem opt)

                        _ ->
                            Nothing

                menuConfig =
                    Styles.setMenuMaxHeightPx (Css.px 390) (Styles.getMenuConfig Styles.bootstrap4)
            in
            Styled.map SelectMsg <|
                Select.view
                    (Select.single selected
                        |> Select.state readyModel.selectState
                        |> Select.menuItems readyModel.items
                        |> Select.placeholder "Select..."
                        |> Select.searchable True
                        |> Select.clearable True
                        |> Select.name readyModel.toModel.name
                        |> Select.setStyles (Styles.setMenuStyles menuConfig Styles.bootstrap4)
                    )

        Error ->
            text ""
