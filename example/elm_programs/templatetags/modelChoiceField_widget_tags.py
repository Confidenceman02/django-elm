from django import template
from ..flags.widgets.modelChoiceField import key, ModelChoiceFieldFlags

register = template.Library()


@register.inclusion_tag("djelm/program.html", takes_context=True, name="render_ModelChoiceFieldWidget")
def render_modelChoiceField(context):
    return {"key": key, "flags": ModelChoiceFieldFlags.parse(context["field"])}


@register.inclusion_tag("djelm/include.html", name="include_ModelChoiceFieldWidget")
def include_modelChoiceField():
    # Generates the script tag for the Widgets/ModelChoiceField.elm program
    return {"djelm_program": "dist/Widgets.ModelChoiceField.js"}
