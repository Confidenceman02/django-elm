from django import template

register = template.Library()

@register.inclusion_tag("main.html", takes_context=True)
def render_main(context):
    # Write your code here in order to render the Main.elm program
    pass

@register.inclusion_tag("include.html")
def include_main():
    # Generates the script tag for the Main.elm program
    return {"djelm_program": "dist/Main.js"}
