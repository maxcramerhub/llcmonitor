from django import forms
from .models import Reviews
from .models import Tutor

class ReviewForm(forms.ModelForm):

    tutor = forms.ModelChoiceField( #needs to be placed before class meta
        queryset=Tutor.objects.all(),
        empty_label="Select a tutor",
        label="Tutor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Reviews
        fields = ['tutor', 'written_review', 'rating']  # include fields
        widgets = {
            'written_review': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'style': 'width: 100%; height: 150px;'}),
            'rating': forms.HiddenInput(),
        }
