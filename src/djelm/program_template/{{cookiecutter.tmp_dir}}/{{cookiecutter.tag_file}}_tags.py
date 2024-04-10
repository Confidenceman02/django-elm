from django import template
from ..flags.{{cookiecutter.tag_file}} import key, {{cookiecutter.program_name}}Flags

register = template.Library()


@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_{{ cookiecutter.tag_file }}(context):
    return {"key": key, "flags": {{cookiecutter.program_name}}Flags.parse(0)}


@register.inclusion_tag("djelm/include.html")
def include_{{ cookiecutter.tag_file }}():
    # Generates the script tag for the {{cookiecutter.program_name}}.elm program
    return {"djelm_program": "dist/{{ cookiecutter.program_name }}.js"}
