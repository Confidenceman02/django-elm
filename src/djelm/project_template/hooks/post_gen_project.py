import os

app_name = "{{cookiecutter.app_name}}"

REMOVE_PATHS = [
    "static/dist/.gitkeep",
    "templates/.gitkeep",
    "templates/{{cookiecutter.app_name}}/.gitkeep",
    "static_src/src/Models/.gitkeep",
    "flags/.gitkeep",
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        os.unlink(path) if os.path.isfile(path) else os.rmdir(path)
