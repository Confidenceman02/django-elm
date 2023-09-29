from django.conf import settings


def get_config(setting_name):
    return {
        "NPM_BIN_PATH": getattr(settings, "NPM_BIN_PATH", "npm"),
    }[setting_name]
