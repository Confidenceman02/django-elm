from django import template
from ..flags.{{cookiecutter.tag_file}} import {{cookiecutter.program_name}}Flags

register = template.Library()


@register.inclusion_tag("{{ cookiecutter.app_name }}/{{ cookiecutter.tag_file }}.html", takes_context=True)
def render_{{ cookiecutter.tag_file }}(context):
    return {"flags": {{cookiecutter.program_name}}Flags.parse(0)}


@register.inclusion_tag("include.html")
def include_{{ cookiecutter.tag_file }}():
    # Generates the script tag for the {{cookiecutter.program_name}}.elm program
    return {"djelm_program": "dist/{{ cookiecutter.program_name }}.js"}
