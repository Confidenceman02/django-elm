"""
URL configuration for example project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.views.generic import TemplateView

from core.views import promotion_view, update_promotion_view


urlpatterns = [
    path("main", TemplateView.as_view(template_name="core/main.html")),
    path("promotion", promotion_view, name="promotion"),
    path(
        "promotion_update/<int:promotion_id>",
        update_promotion_view,
        name="update_promotion",
    ),
    path("__reload__/", include("django_browser_reload.urls")),
]
