from django import forms
from .models import ProductReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['stars', 'content']
        widgets = {
            "stars": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5,
                "style": "border-color: #6a0dad;"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "style": "border-color: #6a0dad;"
            }),
        }
