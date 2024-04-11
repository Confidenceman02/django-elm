# Djelm widgets

## What are they?

You can think of djelm widgets as opinionated but flexible Elm programs, designed in house, to work seamlessly with Django form primitives like [ModelChoiceField]().

Widgets visually extend the style and functionality of the native form elements you would usually get out of the box from django.

The following example is a standard select input django renders for us via the use of [ModelChoiceField](https://docs.djangoproject.com/en/5.0/ref/forms/fields/#django.forms.ModelChoiceField) in a typical, albeit oversimplified, form.

![example](https://Confidenceman02.github.io/djelm/static/dj-mcf.gif)

And here is the default djelm [ModelChoiceField](#modelchoicefield-widget) widget.

![example](https://Confidenceman02.github.io/djelm/static/djelm-mcf.gif)

There are many features that you get in the djelm version that would otherwise require a tremendous amount of custom Javascript to implement yourself.

Djelm also doesn't hide the widget implementations from you, they exist as regular Elm programs in your djelm app that you can modify to create incredible user experiences.

![example](https://Confidenceman02.github.io/djelm/static/djelm-cs-mcf.gif)

> [!NOTE]
> For demonstration purposes, I will referring to a hypothetical djelm app called `elm_programs`

# ModelChoiceField widget

django primitive: ModelChoiceField

Elm dependencies:

- [Confidenceman02/elm-select](https://package.elm-lang.org/packages/Confidenceman02/elm-select/latest/)
- [rtfeldman/elm-css](https://package.elm-lang.org/packages/rtfeldman/elm-css/latest/)

> [!NOTE]
> All Elm dependecies are automatically installed for you

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

The [ModelChoiceField](#modelchoicefield-widget) widget by default is a generic widget that can work with all of your django forms that implement a [forms.ModelChoiceField]() instance.

However, there may be times where you want the widget to look or perform differently based on the model that was used in the queryset.

Variants leverage Elm [Custom Types](https://guide.elm-lang.org/types/custom_types) so that you can, at a type level, know
which model generated the values and also, at a data level, have access to the fields and values of that model.

Let consider following models and forms

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

The widget works with both forms and our respective choices shape in the Elm model looks like the following.

```elm
type alias Options_ =
    { choice_label : String
    , value : String
    , selected : Bool
    }
```

This shape alone doesn't give us enough information to know which type of option we are dealing with, is it a `Course` or `Student` option?

Let's add the variants to the widget flag in `elm_programs/flags/widgets/modelChoiceField.py` file:

```python
from models import Course, Student

# previous
ModelChoiceFieldFlags = Flags(ModelChoiceFieldFlag())

# with variants
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

This gives us pattern matching super powers that we can leverage to customise the widget

```elm
doSomethingWithOption : Options_ -> somethingAwesome
doSomethingWithOption option =
    case option of
        Course data ->
            -- do something awesome with course option
        Student data ->
            -- do something awesome with student option
```

> [!NOTE]
> Only `models.Charfield` model fields are supoprted currently.
