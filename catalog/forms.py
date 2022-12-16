from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('mark',)
        labels = {
            'mark': _('Оценка'),
        }
