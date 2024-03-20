def task_buildimages():
    """buildimages

    Build and push local Docker image.
    """
    return {
        "actions": [
            "cd ops/ci && docker build -t ghcr.io/confidenceman02/django-elm/djelm:5 .",
            "docker push ghcr.io/confidenceman02/django-elm/djelm:5",
        ],
        "targets": [],
    }


def task_install_e2e_browser():
    "Install playwright browser"

    return {"actions": ["playwright install firefox"]}


def task_run_example():
    "startenv"

    return {
        "actions": [
            "cd example && python manage.py migrate",
            "cd example && python manage.py seed",
            "cd example && python manage.py runserver",
        ]
    }


def task_prepare_e2e_tests():
    "startenv"

    return {
        "actions": [
            "cd example && python manage.py migrate",
            "cd example && python manage.py seed",
            "cd example && python manage.py djelm addprogram elm_programs Main",
            "cd example && python manage.py djelm addwidget elm_programs ModelChoiceField --no-deps",
            "cd example && python manage.py runserver",
        ]
    }
