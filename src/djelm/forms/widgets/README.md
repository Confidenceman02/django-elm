# Djelm widgets

## What are they?

Djelm widgets are opinionated but flexible Elm programs, designed in house, that extend the style and functionality of the native html elements you would usually get out of the box from
Django primitives such as [ModelChoiceField](https://docs.djangoproject.com/en/5.0/ref/forms/fields/#django.forms.ModelChoiceField).

> [!NOTE]
> For demonstration purposes, I will be referring to a hypothetical djelm app called `elm_programs`

# ModelChoiceField widget

django primitive: ModelChoiceField

Elm dependencies:

- [Confidenceman02/elm-select](https://package.elm-lang.org/packages/Confidenceman02/elm-select/latest/)
- [rtfeldman/elm-css](https://package.elm-lang.org/packages/rtfeldman/elm-css/latest/)

> [!NOTE]
> All Elm dependecies are automatically installed for you

## Example

![example](https://Confidenceman02.github.io/djelm/static/djelm-mcf.gif)

## Usage

Add the [ModelChoiceField](#modelchoicefield-widget) widget to your djelm app

```bash
python manage.py djelm addwidget elm_programs ModelChoiceField
```

Compile the [ModelChoiceField](#modelchoicefield-widget) widget program

```bash
python manage.py djelm compile elm_programs
```

In your form, declare a custom template for the [forms.ModelChoiceField](https://docs.djangoproject.com/en/5.0/ref/forms/fields/#django.forms.ModelChoiceField) instance

```python
# forms.py
from django import forms
from models import Promotion

class PromotionForm(forms.ModelForm):
    courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        template_name="modelChoiceFieldWidget.html", # <--- custom template
    )

    class Meta:
        model = Promotion
        fields = ["courses"]

```

Load and add the [ModelChoiceField](#modelchoicefield-widget) tags to your custom template.

> [!NOTE]
> Modify the following to suit your template layout

```djangohtml
<!-- modelChoiceFieldWidget.html -->

{% extends "base.html" %}
{% load modelChoiceField_widget_tags %} <--- load
{% block head %}
    {% include_ModelChoiceFieldWidget %} <--- include
{% endblock %}
{% block content %}
    {{ field.label_tag }}
    {% render_ModelChoiceFieldWidget %} <--- render
{% endblock %}
```

## Variants

The [ModelChoiceField](#modelchoicefield-widget) widget is generic and can work with all of your django forms that implement a [forms.ModelChoiceField](https://docs.djangoproject.com/en/5.0/ref/forms/fields/#django.forms.ModelChoiceField) instance.

However, there may be times where you want the widget to look or perform differently based on the model that was used in the queryset, perhaps something like the following.

![example](https://Confidenceman02.github.io/djelm/static/djelm-cs-mcf.gif)

Variants leverage Elm [Custom Types](https://guide.elm-lang.org/types/custom_types) so that you can, at a type level, know
which model generated the values and also, at a data level, have access to the fields and values of that model to enhance the widget as required.

Let's consider the following models and forms

```python
# models.py
from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.first_name

# forms.py
from django import forms
from models import Promotion, School, Course, Student

class PromotionForm(forms.ModelForm):
    courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        template_name="modelChoiceFieldWidget.html",
        empty_label=None
    )

    class Meta:
        model = Promotion
        fields = ["courses"]

class SchoolForm(forms.ModelForm):
    students = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        template_name="modelChoiceFieldWidget.html",
    )

    class Meta:
        model = School
        fields = ["students"]

```

The widget program represents options with a generic type alias, with just enough information to faithfully render the widget for any model queryset:

```elm
type alias Options_ =
    { choice_label : String
    , value : String
    , selected : Bool
    }
```

This type doesn't give us enough information to differentiate the model however i.e. are they `Course` or `Student` options?

Let's add the models as variants to the [ModelChoiceField](#modelchoicefield-widget) widget flag in `elm_programs/flags/widgets/modelChoiceField.py` file:

```python
from models import Course, Student

ModelChoiceFieldFlags = Flags(ModelChoiceFieldFlag(variants=[Course, Student]))
```

We can now generate the model for the widget:

```bash
python manage.py djelm generatemodel elm_programs Widgets.ModelChoiceField
```

Let's see what our types now look like

```elm
type Options_
    = Course Options_Course__
    | Student Options_Student__

type alias Options_Course__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : { name : String, instructor : String }
    }

type alias Options_Student__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : { first_name : String, country : String }
    }
```

This gives us pattern matching super powers that we can leverage to customise the widget program.

```elm
doSomethingWithOption : Options_ -> somethingAwesome
doSomethingWithOption option =
    case option of
        Course data ->
            -- do something awesome with course option
        Student data ->
            -- do something awesome with student option
```

> [!IMPORTANT]
> Django by default includes an empty label option that is not part of a model instance.
> Using variants will cause djelm to trigger a pydantic error due to this.
>
> Make sure you set `empty_label` to `None` on the ModelChoiceField form field to avoid this error.

# ModelMultipleChoiceField widget

django primitive: ModelMultipleChoiceField

Elm dependencies:

- [Confidenceman02/elm-select](https://package.elm-lang.org/packages/Confidenceman02/elm-select/latest/)
- [rtfeldman/elm-css](https://package.elm-lang.org/packages/rtfeldman/elm-css/latest/)

> [!NOTE]
> All Elm dependecies are automatically installed for you

## Example

![example](https://Confidenceman02.github.io/djelm/static/djelm-mmcf.gif)

> [!IMPORTANT]
> For examples and customization options see [ModelChoiceField](#modelchoicefield-widget).
> Under the hood they both work exactly the same.
