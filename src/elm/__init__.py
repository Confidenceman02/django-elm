from django.conf import settings


def get_config(setting_name) -> str:
    return {
        "NODE_PACKAGE_MANAGER": getattr(settings, "NODE_PACKAGE_MANAGER", "pnpm"),
        "ELM_BIN_PATH": getattr(settings, "ELM_BIN_PATH", "elm"),
    }[setting_name]
