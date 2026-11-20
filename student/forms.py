from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class Studentform_data(forms.Form):
    reg_no1 = forms.IntegerField(
        label='Registration number',
        widget=forms.NumberInput(attrs={
            'class': 'field-input',
            'placeholder': 'e.g. 2026001',
            'inputmode': 'numeric',
        }),
    )
    name1 = forms.CharField(
        label='Full name',
        widget=forms.TextInput(attrs={
            'class': 'field-input',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
        }),
    )
    email1 = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={
            'class': 'field-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        }),
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'field-input',
            'autocomplete': 'email',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')



