from django import forms
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    """
    Form for customer or provider to submit a complaint.
    """

    class Meta:
        model = Complaint
        fields = ['subject', 'description']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subject of your complaint'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your complaint in detail...'
            }),
        }


class ComplaintResponseForm(forms.ModelForm):
    """
    Form for admin to respond to a complaint
    and update its status.
    """

    class Meta:
        model = Complaint
        fields = ['status', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your response to this complaint...'
            }),
        } 
