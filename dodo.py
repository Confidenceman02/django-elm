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
