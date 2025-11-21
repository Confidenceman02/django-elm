from django import template
import json

from djelm.settings import ProgramSettings

register = template.Library()


@register.simple_tag
def merge_settings(**kwargs):
    """
    Combines default settings with user-provided settings,
    and returns the result as a JSON string.
    """
    default_settings = ProgramSettings().get_settings()
    passed_settings = kwargs.get("settings", {})

    config = default_settings | passed_settings

    return json.dumps(config)


@register.simple_tag
def default_settings():
    """
    Returns the default program settings as a JSON string.
    """
    default_settings = ProgramSettings().get_settings()

    return json.dumps(default_settings)
