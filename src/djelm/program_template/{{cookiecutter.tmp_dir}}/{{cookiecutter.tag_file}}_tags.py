from django import template
from ..flags.main import flags

register = template.Library()

@register.inclusion_tag("{{ cookiecutter.tag_file }}.html", takes_context=True)
def render_{{ cookiecutter.tag_file }}(context):
    return {"flags": flags }

@register.inclusion_tag("include.html")
def include_{{ cookiecutter.tag_file }}():
    # Generates the script tag for the {{cookiecutter.program_name}}.elm program
    return {"djelm_program": "dist/{{ cookiecutter.program_name }}.js"}
