import os

REMOVE_PATHS = [
    "static/dist/.gitkeep",
    "templates/.gitkeep",
    "static_src/djelm_src/.gitkeep",
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        os.unlink(path) if os.path.isfile(path) else os.rmdir(path)
