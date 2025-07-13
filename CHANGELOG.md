## [0.20.0] - 2025-07-13

### Added

- AliasFlag for resusable tpyes and decoders

## [0.19.1] - 2025-04-29

### Fixed

- Detecting Elm entrypoint files with custom type parameters

## [0.19.0] - 2025-04-15

### Added

- removeprogram strategy

## [0.18.2] - 2025-02-26

### Improved

- Cookiecutter now added as a project dependency

## [0.18.1] - 2025-02-07

### Improved

- All cookiecutter templates now live in the cookiecutters directory.
- cookiecutter templates directly create individual files in the app avoiding unecessary IO.

## [0.18.0] - 2025-02-03

### Added

- addprogramhandlers command

## [0.17.0] - 2024-12-16

### Added

- generatemodels command

## [0.16.1] - 2024-09-18

### Fixed

- Generating compile files when running compile command

## [0.16.0] - 2024-09-08

### Breaking

- djelm_src directory removed from app

All typescript entrypoint files are now managed internally.
If you were adding custom javascript to those files then stay on the previous version.

## [0.15.0] - 2024-07-15

### Added

- FindPrograms strategy

```elm
python manage.py djelm findprograms <djelm_app>
```

## [0.14.0] - 2024-06-25

### Fixed

- Widget model's not generating when their flags change

## [0.13.0] - 2024-06-22

### Added

- ModelMultipleChoiceField widget

## [0.12.0] - 2024-05-20

### Added

- StringFlag now accepts a 'literal' arg for matching string literals
- Generated Elm decoders express the literal validation

```python
# flags

StringFlag(literal="foo")
```

```elm
-- Model
(Decode.string |> Decode.andThen (lit -> if lit = "foo" then Decode.succeed "foo" else Decode.fail "..."))
```

## [0.11.0] - 2024-05-09

### Added

- Compiled programs now esmodule targets
- Include script now targeting `type="module"`

Things should just work but in case you are doing anything with ES modules in the compiled js
the following should set it right:

```bash
python manage.py djelm watch <your-djelm-app>
```

Alternatively you can remove the `.parcel-cache` directory and run:

```bash
python manage.py djelm compile <your-djelm-app>
```

## [0.10.0] - 2024-04-18

### Added

- ModelChoiceField [variants](https://github.com/Confidenceman02/django-elm/blob/main/src/djelm/forms/widgets/README.md)

## [0.9.0] - 2024-04-10

### Breaking

In a created djelm app the `templates` directory is no longer used.

Existing code should still work fine, however it is recommended that they are updated.

For updating existing programs that you have added custom code to, ensure you have saved the files listed as the following method will overwrite them.

- "templatetags/<program_name>\_tags.py"
- "templatetags/<program_name>\_tags.py"
- "flags/<program_name>.py"
- "flags/widgets/<program_name>.py"
- "static_src/src/<program_name>.elm"

run:

```bash
python manage.py djelm addprogram <djelm_app> <existing_program_name>
```

i.e.

```bash
python manage.py djelm addprogram elm_programs Main
```

for widgets

```bash
python manage.py djelm addwidget elm_programs <widget>
```

Once completed you can add back any custom code that existed previously.

#### templatetags

- include.html and <program_name>.html files are now pointing to internal djelm templates.
- The key that the client hydration code uses to initialize a program is now included in the tag.

previous

```python
# <djelm_app>/templatetags/<program_name>_tags.py

@register.inclusion_tag("<app_name>/<program_name>.html", takes_context=True)
def render_<program_name>(context):
    return {"flags": MainFlags.parse("Hello Elm!")}
```

current

```python
# <djelm_app>/templatetags/<program_name>_tags.py

@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_<program_name>(context):
    return {"key": key, "flags": MainFlags.parse("Hello Elm!")}
```

#### flags key

- The client hydration code uses a key to detect server rendered program tags and initialize elm programs. This was
  being encoded into the generated html templates and now is passed as an argument.

previous

```python
# flags/<program_name>.py
<program_name>Flags = Flags(IntFlag())
```

current

```python
key = "<generated_key>"

<program_name>Flags = Flags(IntFlag())
```

## [0.8.0] - 2024-04-08

### Added

- Python to Elm compiler
- CustomTypeFlags support

## [0.7.0] - 2024-04-03

### Fixed

- compilebuild strategy swallowing errors when Elm compiler errors.

## [0.6.0] - 2024-03-27

### Fixed

- generatemodel strategy called from cli ignoring existing program flag
  and instead rendering a default `Int` model.

## [0.5.0] - 2024-03-20

### Added

- Widget strategy for ModelChoiceField
- listwidgets command
- ModelChoiceFieldFlag class
- Browser tests with Playwright
- Example django project setup
- README widget section

### Fixed

- Name clash compiler error

### Breaking

- Top flag module imports

previous

```python
from djelm.flags.main import Flags, IntFlag
```

current

```python
from djelm.flags import Flags, IntFlag
```

- Model alias types now consist of their parent alias name as a prefix
  to avoid name clashes.

previous

```elm
type alias A_
    { b : B_
    }

type alias B_
    { c : String
    }
```

current

```elm
type alias A_
    { b : A_B__
    }

type alias A_B__
    { c : String
    }
```

## [0.4.0] - 2024-02-22

### Fixed

- Extra arg constraints removed from elm strategy

## [0.3.0] - 2024-02-19

### Fixed

- Use subprocess for cookiecutter lazy load
- Add Github workflow for auto publishing on tag push

## [0.2.0] - 2024-02-18

### Added

- Elm watch generates Elm models when flags change.
- Pretty console errors
- Clearer README

## [0.1.0] - 2023-12-25

### Added

- First version to pyPI

[0.20.0]: https://github.com/Confidenceman02/django-elm/compare/0.19.1...0.20.0
[0.19.1]: https://github.com/Confidenceman02/django-elm/compare/0.19.0...0.19.1
[0.19.0]: https://github.com/Confidenceman02/django-elm/compare/0.18.2...0.19.0
[0.18.2]: https://github.com/Confidenceman02/django-elm/compare/0.18.1...0.18.2
[0.18.1]: https://github.com/Confidenceman02/django-elm/compare/0.18.0...0.18.1
[0.18.0]: https://github.com/Confidenceman02/django-elm/compare/0.17.0...0.18.0
[0.17.0]: https://github.com/Confidenceman02/django-elm/compare/0.16.1...0.17.0
[0.16.1]: https://github.com/Confidenceman02/django-elm/compare/0.16.0...0.16.1
[0.16.0]: https://github.com/Confidenceman02/django-elm/compare/0.15.0...0.16.0
[0.15.0]: https://github.com/Confidenceman02/django-elm/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/Confidenceman02/django-elm/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/Confidenceman02/django-elm/compare/0.12.0...0.13.0
[0.12.0]: https://github.com/Confidenceman02/django-elm/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/Confidenceman02/django-elm/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/Confidenceman02/django-elm/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/Confidenceman02/django-elm/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/Confidenceman02/django-elm/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/Confidenceman02/django-elm/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/Confidenceman02/django-elm/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/Confidenceman02/django-elm/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/Confidenceman02/django-elm/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Confidenceman02/django-elm/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Confidenceman02/django-elm/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Confidenceman02/django-elm/releases/0.1.0
