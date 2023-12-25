# DJelm

[![DJelm](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Confidenceman02/django-elm/main/assets/badge/v0.json)](https://github.com/Confidenceman02/django-elm)
[![Actions status](https://Confidenceman02.github.io/djelm/workflows/CI/badge.svg)](https://github.com/Confidenceman02/django-elm/actions)
[![](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Confidenceman02/django-elm/blob/main/LICENSE)

# Elm integration for Django a.k.a. Django + Elm = 💚 DJelm

---

## Why to use

Quite often in a server side rendered Django project you reach a point where part of the UI needs to change. Sometimes that
change is very simple, like a button click that adds or removes a todo item, or perhaps a variety of controls that dynamically updates a map.

Whatever the case, handling these changes typically involves the use of javascript.

Perhaps all you need is a humble event listener to handle a click and update some DOM, but beware, there be dragons! What starts off as humble can easily turn in
to an unmanagable dumpster fire of spaghetti code, bespoke state management and a littering of header script imports to bloated third party javascript you don't
even know if you are using.

The goal for Djelm then is to be a bridge to an island of interactivity, leveraging the full power of Elm for all your bespoke UI that would otherwise be
clunky to build.

## When to use

Djelm is **not intended to be the primary UI** solution for a DJango project, although you will be tempted for it to be so, such is the delightfullness of the Elm language.
In fact I would encourage folks use the following guidelines before leveraging the power of a framework like Elm, or any framework for that matter.

1. Push the Django template conventions to their limit.

   - Django has a truly enormous amount of packages that can help you organise tricky UI for forms, tables, pagination, search etc.
     You get the benefit of these tools being tightly integrated with the Django framework, so explore them in depth.

2. Try out a killer combo such as [HTMX](https://htmx.org/) and [Alpine JS](https://alpinejs.dev/)

   - This combo being able to handle the vast majority of your UI reactivity is entirely conceivable and usually a more light weight approach
     to that of a framework.

3. Try your hardest to justify not using a framework.
   - Despite Djelm going to great lengths to encapsulate complexity, there's no getting around it that adding a framework increases your projects complexity footprint.
     If you realise that some slick UI can be sensibly achieved with the guidelines above, congratulations! You have avoided adding complexity.

I promise that two things will happen if you follow the above advice.

1. You will write far fewer lines of framework code.
2. The framework code that you do end up writing will not only be justifiably fit for purpose, but in the case of Djelm, a robust, correct, reliable joy to maintain!

## Requirements

Python 3.11 or newer with Django >= 4 or newer.

## Elm set up

Djelm will expect the Elm binary to be in your `PATH`.

Head on over to the [installation guide](https://guide.elm-lang.org/install/elm.html) to get the Elm binary on your system.

After installing, let's make sure Elm is ready to go. In your terminal run the command:

```bash
elm
```

You should see a friendly welcome message and some other helpful Elm info.

## Django set up

> [!NOTE]
> This set up guide assumes you have a Django project already set up. If not check out the excellent [Django docs](https://docs.djangoproject.com/en/4.2/intro/tutorial01/) to get one going.

- You will need the `django-elm` package, let's get it with `pip`.

```bash
pip install django-elm
```

- Add the `djelm` app to your `INSTALLED_APPS` in `settings.py`

```python
# settings.py

INSTALLED_APPS = [
        ...,
    "djelm",
]

```

- Optionally set you package manager of choice.

> [!NOTE]
> If you don't set this variable then Djelm will try to use [pnpm](https://pnpm.io/). Use the [install guide](https://pnpm.io/installation) if you would like to use this default and you don't currently have it installed.

```python
# settings.py

NODE_PACKAGE_MANAGER = "yarn"
```

## Your first Elm program

The first thing we will need to do is create a directory where all your elm programs will live. Djelm is fairly opinionated about what lives inside this directory
so for the best experience let's use Djelm commands to create one for us.

From your Django project root:

```bash
python manage.py djelm create elm_programs
```

> [!TIP]
> The `elm_programs` argument is just a name that I give the directory that all my elm programs live in, feel free to call it something else for your project.

If we take a look at our `elm_programs` directory let's see what was created for us.

```bash
elm_programs
├── apps.py
├── elm_programs.djelm
├── flags
├── static
│   └── dist
├── static_src
│   ├── .djelm
│   │   └── compile.js
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

Everything outside of the `static_src` directory should look like a typical Django app, and everything inside of `static_src` should look
like a conventional Elm project, with some extra bits.

Now that we have a place for Elm programs to live let's go ahead and add one!

```bash
python manage.py djelm addprogram elm_programs Main
```

> [!TIP]
> You can change the `Main` argument to whatever makes the most sense for your program. e.g. Map, TodoApp, UserProfile. For the most predictable results when generating a program, ensure you use the
> Elm module naming conventions which you can find [here](https://guide.elm-lang.org/webapps/modules).

Looking at the `elm_programs` directory we can see a few things have been added.

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
│   ├── .djelm
│   │   └── compile.js
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

Jump in to the `src/Main.elm` file in the `elm_programs` directory and what you will see is a simple Elm program. You might be able to work out what this program does just by looking at the `Msg` type!

```elm
type Msg
    = Increment
    | Decrement
```

To actually run this Elm program with Django we will need to compile it, for that we will need to install the node packages defined in the `elm_programs` `package.json` file.

> [!NOTE]
> Elm doesn't actually need node to compile programs. However, Djelm optimzes Elm programs to work with Django templates so a tiny amount of DOM binding code is bundled in.

We can install all node packages with the following command:

```bash
python manage.py djelm npm elm_programs install
```

> [!NOTE]
> The above command runs `pnpm install` in the `elm_programs/static_src` directory. `pnpm` will be substituted for whatever is in the `NODE_PACKAGE_MANAGER` variable in `settings.py`.

alternatively you could do the following:

```bash
cd elm_programs/static_src/ && pnpm install
```

After all packages have installed we can use the Djelm `watch` strategy to compile our Elm programs and watch for changes.

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
│   ├── .djelm
│   │   └── compile.js
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

Let's now actually render something on the screen by adding our `Main` programs tags in a Django template.

> [!NOTE]
> I have added the following `base.html` template to the `elm_programs/templates` directory for demonstration purposes. If you already have a Django project you can just add the relevant tags
> in whatever templates you want to render the elm program.

```html
<!-- base.html -->
{% load static %} {% load static main_tags %}

<!doctype html>
<html lang="en">
  <head>
    <title>Django Tailwind</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    {% include_main %}
  </head>

  <body>
    <div>
      <section>
        <h1>Django + Elm = ❤️</h1>
        <div>{% render_main %}</div>
      </section>
    </div>
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

## Bugs and suggestions

Please see [CONTRIBUTING](CONTRIBUTING.md).

2023 © [Confidencemna02 - A Full Stack Django Developer and Elm shill](#)
