from django import forms

from core.models import Course, Extra, Promotion


class PromotionForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        template_name="core/modelChoiceFieldWidget.html",
        empty_label=None,
    )
    extras = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.all(),
        template_name="core/modelMultipleChoiceFieldWidget.html",
    )

    class Meta:
        model = Promotion
        fields = ["course", "extras"]
