from django import template
from ..flags.main import MainFlags

register = template.Library()


@register.inclusion_tag("elm_programs/main.html", takes_context=True)
def render_main(context):
    return {"flags": MainFlags.parse(0)}


@register.inclusion_tag("include.html")
def include_main():
    # Generates the script tag for the Main.elm program
    return {"djelm_program": "dist/Main.js"}
