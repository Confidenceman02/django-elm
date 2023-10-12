from django import template

register = template.Library()

@register.inclusion_tag("{{ cookiecutter.tag_file }}.html", takes_context=True)
def render_{{ cookiecutter.tag_file }}(context):
    # Write your code here in order to render the {{ cookiecutter.program_name }}.elm program
    pass

