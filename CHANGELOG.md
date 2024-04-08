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

[0.8.0]: https://github.com/Confidenceman02/django-elm/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/Confidenceman02/django-elm/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/Confidenceman02/django-elm/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/Confidenceman02/django-elm/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/Confidenceman02/django-elm/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Confidenceman02/django-elm/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Confidenceman02/django-elm/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Confidenceman02/django-elm/releases/0.1.0
