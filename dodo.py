def task_run_example():
    "startenv"

    return {
        "actions": [
            "cd example && uv run manage.py migrate",
            "cd example && uv run manage.py seed",
            "cd example && uv run manage.py runserver",
        ]
    }


def task_prepare_e2e_tests():
    "startenv"

    return {
        "actions": [
            "cd example && uv run manage.py migrate",
            "cd example && uv run manage.py seed",
            "cd example && uv run manage.py djelm addprogram elm_programs Main",
            "cd example && uv run manage.py djelm addwidget elm_programs ModelChoiceField --no-deps",
            "cd example && uv run manage.py djelm addwidget elm_programs ModelMultipleChoiceField --no-deps",
            "cd example && uv run manage.py runserver 0.0.0.0:8000",
        ]
    }
