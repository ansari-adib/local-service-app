 
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Form for customer to leave a review
    after a completed booking.
    """

    RATING_CHOICES = [
        (5, '5 Stars — Excellent'),
        (4, '4 Stars — Good'),
        (3, '3 Stars — Average'),
        (2, '2 Stars — Poor'),
        (1, '1 Star — Very Bad'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your experience with this service...'
        })
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']