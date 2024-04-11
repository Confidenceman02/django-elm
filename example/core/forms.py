from django import forms

from core.models import Course, Promotion


class PromotionForm(forms.ModelForm):
    courses = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        template_name="core/modelChoiceFieldWidget.html",
        empty_label=None,
    )

    class Meta:
        model = Promotion
        fields = ["courses"]
