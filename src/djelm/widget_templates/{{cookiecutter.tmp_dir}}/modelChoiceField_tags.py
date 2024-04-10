from django import template
from ..flags.widgets.{{cookiecutter.tag_file}} import key, {{cookiecutter.program_name}}Flags

register = template.Library()


@register.inclusion_tag("djelm/program.html", takes_context=True, name="render_{{cookiecutter.program_name}}Widget")
def render_{{ cookiecutter.tag_file }}(context):
    return {"key": key, "flags": {{cookiecutter.program_name}}Flags.parse(context["field"])}


@register.inclusion_tag("djelm/include.html", name="include_{{cookiecutter.program_name}}Widget")
def include_{{ cookiecutter.tag_file }}():
    # Generates the script tag for the Widgets/{{cookiecutter.program_name}}.elm program
    return {"djelm_program": "dist/Widgets.{{ cookiecutter.program_name }}.js"}
