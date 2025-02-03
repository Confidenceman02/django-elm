<img alt="ContourPy" src="https://raw.githubusercontent.com/confidenceman02/django-elm/main/assets/icon.png" width="140">

# Djelm

[![Actions status](https://Confidenceman02.github.io/djelm/workflows/CI/badge.svg)](https://github.com/Confidenceman02/django-elm/actions)
[![](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Confidenceman02/django-elm/blob/main/LICENSE)

> [!NOTE]
> Djelm is an active project and prior to a stable release changes might come hard and fast as we explore and learn the best way to integrate Elm programs into Django.
>
> Much effort is put into the [CHANGELOG](https://github.com/Confidenceman02/django-elm/blob/main/CHANGELOG.md) to describe and advise on all changes between versions so be sure to utilise it when updating to the latest and greatest version.

# Elm integration for Django a.k.a. Django + Elm = 💚

---

## Table of Content

- [The why](#the-why)
- [The when](#the-when)
- [Requirements](#requirements)
- [Elm setup](#elm-setup)
- [Django setup](#django-setup)
- [Djelm setup](#djelm-setup)
- [Your first Elm program](#your-first-elm-program)
  - [create Command](#create-command)
  - [addprogram Command](#addprogram-command)
  - [npm Command](#npm-command)
  - [watch Command](#watch-command)
  - [compile Command](#compile-command)
  - [compilebuild Command](#compilebuild-command)
  - [Template tags](#template-tags)
  - [Flags](#flags)
  - [Flag classes](#flag-classes)
  - [generatemodel Command](#generatemodel-command)
  - [generatemodels Command](#generatemodels-command)
- [JS Interop](#js-interop)
  - [addprogramhandlers Command](#addprogramhandlers-command)
- [Widgets](#widgets)
  - [addwidget Command](#addwidget-command)
  - [listwidgets Command](#addwidget-command)
- [Elm resources](#elm-resources)

# The why

Django is an awesome framework for rapidly building web apps, but it can be tricky to build UI's that require a level of
reactivity unable to
be expressed via templates alone.

Elm is a statically and strongly typed language with an approachable syntax that provides exceptional programming
ergonomics to build highly reactive UI's.
Elm programs are robust, reliable, and famously, delightful to write and maintain!

Djelm provides the bridge for both of these wonderful technologies to converge allowing you to seamlessly build the
dynamic parts of your UI whilst
working with the Django conventions you know and love.

[Back to top](#table-of-content)

# The when

Because djelm is **not intended** to be the primary UI solution for your Django project, the following guidelines serve
as an initial checklist
that will ensure your use of djelm is fit for purpose.

1. Use the Django conventions and tools.

   - The Django ecosystem has many great libraries that can help you organise tricky UI for forms, tables, pagination,
     and search. You get the benefit of these tools not needing a UI framework.

2. Try out a killer combo such as [HTMX](https://htmx.org/) and [Alpine JS](https://alpinejs.dev/).

   - This combo being able to handle a huge of amount of your UI reactivity is entirely conceivable, however, consider
     the following.
     - HTMX: Ensure your UI/UX won't suffer as a result of a roundtrip to the server.
     - Alpine JS: If you find yourself writing app logic akin to that of a framework, djelm is likely a far better option.

[Back to top](#table-of-content)

# Requirements

- Elm 0.19.1
- Python >=3.11
- Django >= 4.2
- Node >= 16.4

[Back to top](#table-of-content)

# Elm setup

Djelm will expect the Elm binary to be in your `PATH`.

Head on over to the [installation guide](https://guide.elm-lang.org/install/elm.html) to get the Elm binary on your
system.

After installing, let's make sure Elm is ready to go. In your terminal run the command:

```bash
elm
```

You should see a friendly welcome message and some other helpful Elm info.

[Back to top](#table-of-content)

# Django setup

If you don't have a Django project ready to go, we will need to take care of some initial setup.

It's best practice to create a python virtual environment:

```bash
python -m venv venv
```

Then let's start the virtual environment:

```bash
source venv/bin/activate
```

Let's get the Django package with pip:

```bash
pip install django
```

Create the django project:

```bash
django-admin startproject djelmproject && cd djelmproject
```

Lets look at what `startproject` created:

```bash
djelmproject
├── manage.py
├── djelmproject
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
```

[Back to top](#table-of-content)

# Djelm setup

You will need the djelm package, let's get it with `pip`.

```bash
pip install djelm
```

Add the djelm app to your `INSTALLED_APPS` in `settings.py`

```python
# settings.py

INSTALLED_APPS = [
    ...,
    "djelm",
]

```

Optionally set your package manager of choice.

> [!NOTE]
> If you don't set this variable then djelm will try to use [pnpm](https://pnpm.io/). Use
> the [install guide](https://pnpm.io/installation) if you would like to use this default and you don't currently
> have [pnpm](https://pnpm.io/) installed.
>
> We **highly** recommend you use `pnpm` as it doesn't install node package peer dependencies, and usually provides a hassle free performant experience.

```python
# settings.py

NODE_PACKAGE_MANAGER = "yarn"  # npm, pnpm (default)
```

[Back to top](#table-of-content)

# Your first Elm program

## `create` Command

The first thing we will need to do is create a directory where all our Elm programs will live. Djelm is fairly
opinionated about what lives inside this directory so for the best experience let's use the `create` command.

From your Django project root:

```bash
python manage.py djelm create elm_programs
```

> [!TIP]
> The `elm_programs` argument is just a name that I give the app that all my Elm programs live in, feel free to
> call it something else for your project. For the purposes of this tutorial I will refer to the `elm_programs` app.

If we take a look at our `elm_programs` app directory let's see what was created for us.

```bash
elm_programs
├── apps.py
├── elm_programs.djelm
├── flags
├── static
│   └── dist
├── static_src
│   ├── .gitignore
│   ├── elm.json
│   ├── package.json
│   └── src
│       └── Models
└── templatetags
    └── __init__.py
```

What you are seeing is the directory structure required for djelm to seamlessly work with both Django and Elm.

Everything outside of the `static_src` directory should look like a typical Django app, and everything inside
of `static_src` should look like a conventional Elm project, with some extra bits.

## `addprogram` Command

Now that we have a place for Elm programs to live let's go ahead and add one!

```bash
python manage.py djelm addprogram elm_programs Main
```

> [!TIP]
> You can change the `Main` argument to whatever makes the most sense for your program, like `Map`, `TodoApp`, `UserProfile`.
>
> For the most predictable results when running the `addprogram` command, ensure you use the
> Elm module naming conventions which you can find [here](https://guide.elm-lang.org/webapps/modules).

Looking at the `elm_programs` app directory again we can see a few things have been added.

> [!NOTE]
> Added files marked with \*

```bash
elm_programs
├── apps.py
├── elm_programs.djelm
├── flags
│   └── main.py *
├── static
│   └── dist
├── static_src
│   ├── .gitignore
│   ├── elm.json
│   ├── package.json
│   └── src
│       ├── Main.elm *
│       └── Models
│           └── Main.elm *
└── templatetags
    ├── __init__.py
    └── main_tags.py *
```

Jump in to the `static_src/src/Main.elm` file in the `elm_programs` directory and what you will see is a simple Elm
program. You
might be able to work out what this program does just by looking at the `Msg` type!

```elm
type Msg
    = Increment
    | Decrement
```

## `npm` Command

To actually run this Elm program with Django we will need to compile it, for that we will need to install the node
packages defined in the `elm_programs` `package.json` file.

> [!NOTE]
> Elm doesn't actually need node to compile programs. However, djelm optimzes Elm programs to work with Django templates
> so a tiny amount of DOM binding code is bundled in.

We can install all node packages with the following command:

```bash
python manage.py djelm npm elm_programs install
```

> [!NOTE]
> The above command runs `pnpm install` in the `elm_programs/static_src` directory. `pnpm` will be substituted for
> whatever is in the `NODE_PACKAGE_MANAGER` variable in `settings.py`.

alternatively you could do the following:

```bash
cd elm_programs/static_src/ && pnpm install
```

More generally, you can use any arguments you want for the `npm` command after the `elm_programs` argument:

```bash
# pnpm, yarn

python manage.py djelm npm elm_programs add -D some-cool-npm-package

# npm

python manage.py djelm npm elm_programs install -D some-cool-npm-package
```

## `watch` Command

After all node packages have installed we can use the djelm `watch` strategy to compile our Elm programs and watch for
changes.

```bash
python manage.py djelm watch elm_programs
```

You should see some output like the following:

```bash
 Built 2 bundles in 100ms!
```

Let's take a look at what changed.

```bash
elm_programs
├── apps.py
├── elm_programs.djelm
├── flags
│   └── main.py
├── static
│   ├── dist
│   │   └── Main.47ea7fa8.js *
│   │   └── Main.47ea7fa8.js.map *
│   │   └── Main.js *
│   │   └── Main.js.map *
├── static_src
│   ├── .gitignore
│   ├── elm.json
│   ├── package.json
│   └── src
│       ├── Main.elm
│       └── Models
│           └── Main.elm
└── templatetags
    ├── __init__.py
    └── main_tags.py

```

Djelm compiled our `Main.elm` program and bundled it up for us in a place where Django can work with it, awesome!

## `compile` Command

To compile our programs as a one off command we can use the following:

```bash
python manage.py djelm compile elm_programs
```

## `compilebuild` Command

Use the `compilebuild` command for generating production quality assets.

From the command line run:

```bash
python manage.py djelm compilebuild elm_programs
```

> [!TIP]
> After you have compiled your Elm programs for a production environment, it is advised that you
> remove the `static_src` directory as it will contain cache files and node modules that you probably
> don't want sitting on your Django production server taking up space.

## Template tags

Let's now actually render something in the browser by adding our `Main` programs tags to a Django template.

> [!NOTE]
> I have added the following `base.html` and `main.html` templates to a `elm_programs/templates` directory for demonstration purposes.
> You will need to create this directory if you havent done so already.
>
> If you already have a django project you can just add the tags into whatever templates you want to render the elm program.

```html
<!-- base.html -->

<!doctype html>
<html lang="en">
  <head>
    <title>Djelm</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    {% block head %}{% endblock %}
  </head>
  <body>
    {% block content %}{% endblock %}
  </body>
</html>
```

```djangohtml
<!-- main.html -->

{% extends "base.html" %}
{% load static %}
{% load static main_tags %}
{% block head %}
    {% include_main %}
{% endblock %}
{% block content %}
    <h1>Django + Elm = ❤️</h1>
    {% render_main %}
{% endblock %}
```

Then we can point a url to the `main.html` template file.

```python
# urls.py
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="main.html")),
]
```

We can now start the Django server.

```bash
python manage.py runserver
```

Head on over to `http://127.0.0.1:8000/` and Voilà!

![example](https://Confidenceman02.github.io/djelm/static/djelm.gif)

## Flags

> [!NOTE]
> Flags are a critical paradigm in Elm so I recommend checking
> out [these docs](https://guide.elm-lang.org/interop/flags.html) for a great introduction to them.

Flags are the way we pipe data from our Django server in to our Elm programs. They very much define the contract between
python values and an Elm model.

Let's analyze the default program we generated earlier which simply increments and decrements an integer.

You will notice if we look at the running program in the browser that it starts off with an integer of `0`, but `0` is
not hardcoded anywhere in the Elm program.
So where does it come from?

This value actually comes bound to our render tag when we server render the template, and is passed to the Elm program
when it is initialized on the client,
as a flag value.

Check out the `elm_programs/templatetags/main_tags.py` file that was generated for you:

```python
@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_main(context):
    return {"key": key, "flags": MainFlags.parse(0)}
```

Those experienced with Django might be having an 'Aha!' moment right now but don't worry if thats not the case,
I'll explain everything.

This `0` value is set from the `render_main` tag function as a default, the actual values you will want to pass your Elm
programs are much more likely to originate in your Django views like the following example:

```python
# views.py

def counter_view(request: AuthedHttpRequest):
    context = {
        "counter_start": 0,
    }

    return render(request, "base.html", context)
```

The context that was set in the view is available to us from the `render_main` tag function which we can
call `MainFlags` with:

```python
# main_tags.py

@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_main(context):
    return {"key": key, "flags": MainFlags.parse(context["counter_start"])}
```

Whilst in this example we are hardcoding a value of `0`, you really can pass it any `int` you want, perhaps an ID from a
database
model or some other computed value.

The one constraint you have is that it must be an `int`, which is perfect for our default Elm
program, but not very flexible for other types of Elm programs you might like to build.

> [!NOTE]
> If you are not sure what Django tags are check out the
> docs [here](https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/).

Let's try passing something that isn't an `int` and see what happens:

```python
# main_tags.py

@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_main(context):
    return {"key": key, "flags": MainFlags.parse("Hello Elm!")}
```

What you should be seeing is a server error, but why? Let's find out!

## Flag classes

If we inspect the `MainFlags` function in `elm_programs/flags/main.py` we will see the following:

```python
MainFlags = Flags(IntFlag())
```

The `Flags` class takes as it's argument the flags shape that you want to pass to the `Main.elm` program
when it initializes.

We are using the `IntFlag` class which enforces that the type of value that can be passed to our `Main.elm` program is
an `int`.
If we pass anything other than an `int` to `MainFlags.parse` an error will be raised just like the one we saw when we used the
value `MainFlags.parse("hello Elm!")`.

The `IntFlag` class is intrinsic to the model that exists in our `Main.elm` program as seen
in `elm_programs/static_src/src/Models/Main.elm`:

```elm
type alias ToModel =
    Int


toModel : Decode.Decoder ToModel
toModel =
    Decode.int
```

The `Main.elm` program uses this model to protect us from any uninvited flags that might show up at runtime as seen in `elm_programs/static_src/src/Main.elm`:

```elm
init : Value -> ( Model, Cmd Msg )
init f =
    case decodeValue toModel f of
        Ok m -> -- Flag decoded to an Int, Success!
            ( Ready m, Cmd.none )

        Err _ -> -- Flag failed to decode to an Int, Error!
            ( Error, Cmd.none )
```

To summarize, we get compile and runtime guarantees that our program will behave as we expect. This is what makes Elm programs
incredibly robust and nearly impossible to produce a runtime exception with.

You can check out all the python flags you can use to express your data shape [here](https://github.com/Confidenceman02/django-elm/blob/main/src/djelm/flags/README.md).

## `generatemodel` Command

Our python flag classes have a little trick up their sleeve that makes keeping both our python and Elm flag contracts in
sync for us.

We can see that in the `elm_programs/static_src/src/Models/Main.elm` module we have the following comment:

```elm
{-| Do not manually edit this file, it was auto-generated by djelm
<https://github.com/Confidenceman02/django-elm>
-}
```

That's right! Djelm makes it uneccessary to ever need to write your own flag decoders, which can be a hefty task if the
shape of your flags is complicated.
Whatever we define as our flags shape in Python will determine the decoders we find in our Elm program.

Let's put this to the test and change the `IntFlag` class to something else for our default program:

```python
MainFlags = Flags(StringFlag())
```

Then in the console run:

```bash
python manage.py djelm generatemodel elm_programs Main
```

> [!NOTE]
> If you have run the `watch` command, djelm will automatically detect flag changes and generate the models for you.

Looking in `elm_programs/static_src/src/Models/Main.elm` you can see our decoders have changed to handle a `String`
value:

```elm
type alias ToModel =
    String


toModel : Decode.Decoder ToModel
toModel =
    Decode.string
```

We can get more adventurous to really see the heavy lifting djelm is doing for us:

```python
MainFlags = Flags(
    ObjectFlag(
        {
            "geometry": ListFlag(ListFlag(FloatFlag())),
            "token": NullableFlag(StringFlag()),
            "someObject": ObjectFlag({"hello": StringFlag(), "elm": StringFlag()}),
        }
    )
)
```

And the result of running `python manage.py djelm generatemodel elm_programs Main`:

```elm
type alias ToModel =
    { geometry : (List (List Float))
    , token : Maybe String
    , someObject : SomeObject_
    }

type alias SomeObject_ =
    { hello : String
    , elm : String
    }


toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |>  required "geometry" (Decode.list (Decode.list Decode.float))
        |>  required "token" (Decode.nullable Decode.string)
        |>  required "someObject" someObject_Decoder

someObject_Decoder : Decode.Decoder SomeObject_
someObject_Decoder =
    Decode.succeed SomeObject_
        |>  required "hello" Decode.string
        |>  required "elm" Decode.string

```

> [!TIP]
> The default Elm program we generated will fail to compile when performing the model changes above.
>
> To help you understand why it failed you can run the [compile](#compile-command) command and experience first hand
> the beauty that is an Elm compiler message.

## `generatemodels` Command

This command let's you do the same thing as the [generatemodel](#generatemodel-command) command except that
you don't need to pass it a specific program name. It will generate models for all your programs.

# JS Interop

Elm isolates your programs from interacting directly with Javascript, but there are numerous reasons why you might need
to utilise Javascript in your programs.

Perhaps you need to use Javascript libraries, tools or browser API's? Whatever the case, Elm
provides JS interop through ports which you can read more about [here](https://guide.elm-lang.org/interop/ports).

## `addprogramhandlers` Command

Creates a handler module with callbacks that hook in to Elm's port functionality for a given program.
Djelm handles bundling the module with the compiled program for you.

Let's assume we have already created an app called `elm_programs` and a program called `Main` inside of it.

The result of calling `python manage.py djelm addprogramhandlers elm_programs Main` adds the module:

```bash
elm_programs/
├── apps.py
├── elm_programs.djelm
├── flags/
├── static/
├── static_src/
│   ├── .gitignore
│   ├── elm.json
│   ├── package.json
│   └── src/
│       ├── Main.elm
│       ├── Main.handlers.ts *
│       └── Models/
└── templatetags
```

If we take a look at the contents of this module we can see a single function:

```ts
// https://guide.elm-lang.org/interop/ports
export function handlePorts(ports): void {
  console.warn("'handlePorts' Not implemented for 'Main.elm'");
}
```

This function is where you would send and subscribe to the ports configured for the `Main.elm` program.

Let's subscribe to a port called `sendMessage` and `console.log` the argument in the callback.

```ts
// https://guide.elm-lang.org/interop/ports
export function handlePorts(ports): void {
  ports.sendMessage.subscribe((msg) => {
    console.log(msg);
  });
}
```

The port `sendMessage` doesn't currently exist in `Main.elm` so let's set it up now.

First we turn the module into a port module, which means it can work with ports:

```elm
-- Main.elm

module Main exposing (..) -- before
port module Main exposing (..) -- after
```

Then we can add our port anywhere we like in the module:

```elm
-- Main.elm
port module Main exposing (..)

-- ports
port sendMessage : String -> Cmd msg
```

To use our `sendMessage` port, we can call it from our `update` function as a `Cmd`. Let's send it everytime we `Increment` or `Decrement`
the counter.

```elm
-- Main.elm

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case model of
        Ready m ->
            case msg of
                Increment ->
                    ( Ready (m + 1), sendMessage "increment")

                Decrement ->
                    ( Ready (m - 1), sendMessage "decrement")

        _ ->
            ( model, Cmd.none )

-- ports
port sendMessage : String -> Cmd msg
```

Use the [compile-command](#compile-command) to compile the program.

> [!NOTE]
> If you have run the `watch` command, djelm will automatically compile the program for you.

Checking the browser we can see our port in action. Nice!

![example](https://Confidenceman02.github.io/djelm/static/django-ports.gif)

This handlers module can also be used to add any other javascript that relates to your given program.

# Widgets

Djelm widgets are feature rich, highly dynamic and customizable programs we can use to supercharge our UI's.

The widgets are added and live inside your app similar to that of a regular program that was added with the [addprogram](#addprogram-command) command.
The key difference being that they are purpose built, handsomely styled, and ready to be used straight out of the box.

Let's consider this simple model and form.

```python
# models.py
from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Promotion(models.Model):
    courses = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)

# forms.py
from django import forms

class PromotionForm(forms.ModelForm):
    courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
    )

    class Meta:
        model = Promotion
        fields = ["courses"]
```

Django will conveniently render a completely usable UI with very little effort from us.

![example](https://Confidenceman02.github.io/djelm/static/dj-mcf.gif)

It's a great start but we want something more customizable, and a fair bit fancier. It's widget time!

## `listwidgets` Command

Let's see a list of all the djelm widgets

```bash
python manage.py djelm listwidgets
```

The `ModelChoiceField` widget from this list seems like the one we want.

## `addwidget` Command

Let's add the widget to our `elm_programs` app.

```bash
python manage.py djelm addwidget elm_programs ModelChoiceField
```

We will also need to compile the widget program before we can use it.

```bash
python manage.py djelm compile elm_programs
```

> [!NOTE]
> If you have run the [watch](#watch-command) command, djelm will automatically compile the program for you.

Now that we have a widget program to render let's set a custom template for our form field.

```python
# forms.py
from django import forms

class PromotionForm(forms.ModelForm):
    courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        template_name="modelChoiceFieldWidget.html", # <--- Added
    )

    class Meta:
        model = Promotion
        fields = ["courses"]
```

Let's now create that custom template.

```djangohtml
<!-- modelChoiceFieldWidget.html -->

{% extends "base.html" %}
{% load modelChoiceField_widget_tags %}
{% block head %}
    {% include_ModelChoiceFieldWidget %}
{% endblock %}
{% block content %}
    {{ field.label_tag }}
    {% render_ModelChoiceFieldWidget %}
{% endblock %}
```

Now that's pretty handsome!

![example](https://Confidenceman02.github.io/djelm/static/djelm-mcf.gif)

We get a nice style and feature improvement over the default input Django gives us, but can we do better?

Yes we can!

Because widget programs are just normal Elm programs that live inside your djelm app, you have complete control
to customize them as you see fit should they not quite fit your branding or presentational requirements.

Let's delight our users by giving them more information about their choices.

![example](https://Confidenceman02.github.io/djelm/static/djelm-cs-mcf.gif)

That's a good looking widget!

> [!NOTE]
> For specific documentation and advanced features for widgets, check out the widget [documentation](https://github.com/Confidenceman02/django-elm/blob/main/src/djelm/forms/widgets/README.md).

[Back to top](#table-of-content)

## Elm resources

- [Official Elm site](https://elm-lang.org/)

  You can find a wonderful introduction to Elm, as well as all the information required to start writing elm programs.
  There is also an [online editor](https://elm-lang.org/try) to try out writing your own programs from scratch or from
  example programs.

- [Elm community Slack](https://elm-lang.org/community/slack)

  The official place for Elm news, jobs, and genreal chit chat.

- [Elm in action](https://www.manning.com/books/elm-in-action)

  By far the most comprehensive book on Elm that exists, written by the mighty Richard Feldman, he will take you from
  beginner to expert.

- [Front end Masters course](https://frontendmasters.com/courses/intro-elm/)

  Here's that Richard Feldman guy again! Richard explores all the juicy bits of Elm in a very high quality presentation.

- [Elm discourse](https://discourse.elm-lang.org/)

  Join our wonderful and friendly Elm forum community! Ask questions, check out what people are working on, or just just
  say hi!

- [Incremental Elm](https://incrementalelm.com/chat/)

  The most experienced and smartest of our community tend to hang in here. Extremely welcoming, and lots of great
  channels to join.

[Back to top](#table-of-content)

2023 © [Confidenceman02 - A Full Stack Django Developer and Elm shill](#)
