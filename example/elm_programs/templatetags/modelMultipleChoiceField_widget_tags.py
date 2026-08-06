from django import template
from ..flags.widgets.modelMultipleChoiceField import key, ModelMultipleChoiceFieldFlags

register = template.Library()


@register.inclusion_tag("djelm/program.html", takes_context=True, name="render_ModelMultipleChoiceFieldWidget")
def render_modelMultipleChoiceField(context):
    return {"key": key, "flags": ModelMultipleChoiceFieldFlags.parse(context["field"])}


@register.inclusion_tag("djelm/include.html", name="include_ModelMultipleChoiceFieldWidget")
def include_modelMultipleChoiceField():
    # Generates the script tag for the Widgets/ModelMultipleChoiceField.elm program
    return {"djelm_program": "dist/Widgets.ModelMultipleChoiceField.js"}
