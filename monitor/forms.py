from django import forms
from .models import Reviews, Tutor, Class

class ReviewForm(forms.ModelForm):

    tutor = forms.ModelChoiceField( #needs to be placed before class meta
        queryset=Tutor.objects.all(),
        empty_label="Select a tutor (optional)",
        label="Tutor (Optional)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select p-4 shadow-sm'})
    )
    
    class Meta:
        model = Reviews
        fields = ['tutor', 'written_review', 'rating']  # class and subject will be auto-populated
        widgets = {
            'written_review': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'style': 'width: 100%; height: 150px;', 'class': 'form-control shadow-sm'}),
            'rating': forms.HiddenInput(),
        }
