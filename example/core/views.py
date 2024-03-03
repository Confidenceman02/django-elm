from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from core.forms import PromotionForm
from core.models import Promotion


# Create your views here.
def promotion_view(request: HttpRequest) -> HttpResponse:
    context = {"form": PromotionForm()}
    if request.method == "POST":
        form = PromotionForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect("update_promotion", promotion_id=instance.id)
        return render(request, "core/promotion_form.html", context)
    else:
        return render(request, "core/promotion_form.html", context)


def update_promotion_view(request: HttpRequest, promotion_id: int) -> HttpResponse:
    model = get_object_or_404(Promotion.objects.filter(id=promotion_id))
    context = {"form": PromotionForm(instance=model)}
    return render(request, "core/promotion_form.html", context)
