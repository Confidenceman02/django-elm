from django import template
from djelm.settings import ProgramSettings
from ..flags.main import key, MainFlags

register = template.Library()


@register.inclusion_tag("djelm/program.html", takes_context=True)
def render_main(context):
    return {
        "key": key,
        "flags": MainFlags.parse(0),
        "settings": ProgramSettings()
        .with_setting({"singleton": True})
        .with_setting({"name": "special-variant"})
        .get_settings(),
    }


@register.inclusion_tag("djelm/include.html")
def include_main():
    # Generates the script tag for the Main.elm program
    return {"djelm_program": "dist/Main.js"}
