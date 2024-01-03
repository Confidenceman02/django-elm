# Djelm

[![Djelm](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Confidenceman02/django-elm/main/assets/badge/v0.json)](https://github.com/Confidenceman02/django-elm)
[![Actions status](https://Confidenceman02.github.io/djelm/workflows/CI/badge.svg)](https://github.com/Confidenceman02/django-elm/actions)
[![](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Confidenceman02/django-elm/blob/main/LICENSE)

# Elm integration for Django a.k.a. Django + Elm = 💚 Djelm

---

## Table Of Content

- [The why](#the-why)
- [The when](#the-when)
- [Requirements](#requirements)
- [Elm setup](#elm-setup)
- [Django setup](#django-setup)
- [Your first Elm program](#your-first-elm-program)
  - [create Command](#create-command)
  - [addprogram Command](#addprogram-command)
  - [watch Command](#watch-command)
  - [compile Command](#compile-command)
  - [compilebuild Command](#compilebuild-command)
  - [Template tags](#template-tags)
  - [Flags](#flags)
  - [Flag classes](#flag-builders)
  - [generatemodel Command](#generating-elm-decoders)

# The why

Elm is a static, strongly typed language with an approachable syntax that provides exceptional programming ergonomics to build highly reactive UI's
that are robust, reliable, and famously, delightful to write and maintain.

# The when

Djelm is intended to used as a specialised framework for you to build the highly dynamic pieces of your UI.

Because Djelm is not intended to be the primary UI solution for your project, the following guidelines serve as an initial checklist
that will ensure your use of Djelm is fit for purpose.

1. Push the Django template conventions to their limit.

   - Django has a truly enormous amount of packages that can help you organise tricky UI for forms, tables, pagination,
     and search. You get the benefit of these tools being tightly integrated with the Django framework, so explore them in depth.

2. Try out a killer combo such as [HTMX](https://htmx.org/) and [Alpine JS](https://alpinejs.dev/).

   - This combo being able to handle the vast majority of your UI reactivity is entirely conceivable and usually a more straightforward approach.

# Requirements

Python 3.11 or newer with Django >= 4 or newer.

# Elm setup

Djelm will expect the Elm binary to be in your `PATH`.

Head on over to the [installation guide](https://guide.elm-lang.org/install/elm.html) to get the Elm binary on your
system.

After installing, let's make sure Elm is ready to go. In your terminal run the command:

```bash
elm
```

You should see a friendly welcome message and some other helpful Elm info.

# Django setup

> [!NOTE]
> This guide assumes you have a Django project already set up or you already know how to create one. If not, check out the
> excellent [Django docs](https://docs.djangoproject.com/en/4.2/intro/tutorial01/) to get one going.

You will need the `djelm` package, let's get it with `pip`.

```bash
pip install djelm
```

Add the `djelm` app to your `INSTALLED_APPS` in `settings.py`

```python
# settings.py

INSTALLED_APPS = [
    ...,
    "djelm",
]

```

Optionally set your package manager of choice.

> [!NOTE]
> If you don't set this variable then Djelm will try to use [pnpm](https://pnpm.io/). Use
> the [install guide](https://pnpm.io/installation) if you would like to use this default and you don't currently
> have [pnpm](https://pnpm.io/)
> installed.

```python
# settings.py

NODE_PACKAGE_MANAGER = "yarn"
```

# Your first Elm program

## `create` Command

The first thing we will need to do is create a directory where all your Elm programs will live. Djelm is fairly
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
│   ├── djelm_src
│   ├── elm.json
│   ├── package.json
│   └── src
│       └── Models
├── templates
│   └── include.html
└── templatetags
    └── __init__.py
```

What you are seeing is the directory structure required for Djelm to seamlessly work with both Django and Elm.

Everything outside of the `static_src` directory should look like a typical Django app, and everything inside
of `static_src` should look like a conventional Elm project, with some extra bits.

## `addprogram` Command

Now that we have a place for Elm programs to live let's go ahead and add one!

```bash
python manage.py djelm addprogram elm_programs Main
```

> [!TIP]
> You can change the `Main` argument to whatever makes the most sense for your program. e.g. `Map`, `TodoApp`, `UserProfile`.
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
│   ├── djelm_src
│   │   └── Main.ts *
│   ├── elm.json
│   ├── package.json
│   └── src
│       ├── Main.elm *
│       └── Models
│           └── Main.elm *
├── templates
│   ├── include.html
│   └── main.html *
└── templatetags
    ├── __init__.py
    └── main_tags.py *
```

Jump in to the `static_src/src/Main.elm` file in the `elm_programs` directory and what you will see is a simple Elm program. You
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
> Elm doesn't actually need node to compile programs. However, Djelm optimzes Elm programs to work with Django templates
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

## `watch` Command

After all node packages have installed we can use the Djelm `watch` strategy to compile our Elm programs and watch for
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
│   ├── djelm_src
│   │   └── Main.ts
│   ├── elm.json
│   ├── package.json
│   └── src
│       ├── Main.elm
│       └── Models
│           └── Main.elm
├── templates
│   ├── include.html
│   └── main.html
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

Let's now actually render something in the browser by adding our `Main` programs tags in a Django template.

> [!NOTE]
> I have added the following `base.html` template to the `elm_programs/templates` directory for demonstration purposes.
> If you already have a Django project you can just add the tags in whatever templates you want to render the Elm program.

```html
<!-- base.html -->
{% load static %}{% load static main_tags %}
<!doctype html>
<html lang="en">
  <head>
    <title>Djelm</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    {% include_main %}
  </head>

  <body>
    <h1>Django + Elm = ❤️</h1>
    {% render_main %}
  </body>
</html>
```

Then we can point a url to the template file we just created.

```python
# urls.py
urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html")),
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

This value actually comes bound to our render tag when we server render the template, and is passed to the Elm program when it is initialized on the client,
as a flag value.

Check out the `elm_programs/templatetags/main_tags.py` file that was generated for you:

```python
@register.inclusion_tag("main.html", takes_context=True)
def render_main(context):
    return {"flags": MainFlags.parse(0)}
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

The context that was set in the view is available to us from the `render_main` tag function which we can call `MainFlags` with:

```python
# main_tags.py

@register.inclusion_tag("main.html", takes_context=True)
def render_main(context):
    return {"flags": MainFlags.parse(context["counter_start"])}
```

Whilst in this example we are hardcoding a value of `0`, you really can pass it any `int` you want, perhaps an ID from a database
model or some other computed value.

The one constraint you have is that it must be an `int`, which is perfect for our default Elm
program, but not very flexible for other types of Elm programs you might like to build.

> [!NOTE]
> If you are not sure what Django tags are check out the docs [here](https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/).

Let's try passing something that isn't an `int` and see what happens:

```python
# main_tags.py

@register.inclusion_tag("main.html", takes_context=True)
def render_main(context):
    return {"flags": MainFlags.parse("hello Elm!")}
```

What you should be seeing is a server error, but why? Let's find out!

## Flag classes

If we inspect the `MainFlags` function in `elm_programs/flags/main.py` we will see the following:

```python
MainFlags = Flags(IntFlag())
```

The `Flags` class takes as it's argument the flags shape that you want to pass to the `Main.elm` program
when it initializes.

We are using the `IntFlag` class which enforces that the type of value that can be passed to our `Main.elm` program is an `int`.
If we pass anything other than an `int` to `MainFlags` an error will be raised just like the one we saw when we used the value `MainFlags.parse("hello Elm!")`.

The `IntFlag` class is also directly related to the contract that exists in our Elm program as seen in `elm_programs/static_src/src/Models/Main.elm`:

```elm
type alias ToModel =
    Int


toModel : Decode.Decoder ToModel
toModel =
    Decode.int
```

What this code reveals is that our `Main.elm` program on initialization will only accept flags that are of type `Int`. A successful
decoding of the flag to an `Int` will thus produce a model of `Int` which agrees perfectly with the python flag definitions.

What we end up with is a very strong contract for both the Django server and the Elm program. This workflow ensures that data is being
validated on both sides.

Elm takes this to the next level by forcing you to handle the possibility of the flag not being an `Int` on initialization as seen in `elm_programs/static_src/src/Main.elm`:

```elm
init : Value -> ( Model, Cmd Msg )
init f =
    case decodeValue toModel f of
        Ok m ->
            ( Ready m, Cmd.none )

        Err _ ->
            ( Error, Cmd.none )
```

The runtime guarantees as a result of this is what makes Elm programs incredibly robust and nearly impossible to produce runtime exceptions.

## `generatemodel` Command

Our python flag classes have a little trick up their sleeve that makes keeping both our python and Elm flag contracts in sync for us.

We can see that in the `elm_programs/static_src/src/Models/Main.elm` module we have the following comment:

```elm
{-| Do not manually edit this file, it was auto-generated by djelm
<https://github.com/Confidenceman02/django-elm>
-}
```

That's right! Djelm makes it uneccessary to ever need to write your own flag decoders, which can be a hefty task if the shape of your flags is
complicated. Whatever we define as our flag shape in Python will determine the decoders we find in our Elm program.

Let's put this to the test and change the `IntFlag` class to something else for our default program:

```python
MainFlags = Flags(StringFlag())
```

Then in the console run:

```bash
python manage.py djelm generatemodel elm_programs Main
```

Looking in `elm_programs/static_src/src/Models/Main.elm` you can see our decoders have changed to handle a `String` value:

```elm
type alias ToModel =
    String


toModel : Decode.Decoder ToModel
toModel =
    Decode.string
```

We can get more adventurous to really see the heavy lifting Djelm is doing for us:

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

2023 © [Confidenceman02 - A Full Stack Django Developer and Elm shill](#)
