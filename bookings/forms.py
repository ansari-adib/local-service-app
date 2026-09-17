from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    """
    Form for customers to create a booking.
    """

    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Booking
        fields = [
            'booking_date',
            'time_slot',
            'address',
            'city',
            'notes'
        ]
        widgets = {
            'time_slot': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address where service is needed'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions for the provider (optional)'
            }),
        }


class BookingRejectionForm(forms.Form):
    """
    Form for provider to give reason when rejecting a booking.
    """

    rejection_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please give a reason for rejection...'
        })
    )