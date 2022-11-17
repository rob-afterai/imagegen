from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Dataset


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = (
            'no_images',
            'image_height',
            'image_width',
            'image_extension',
            'color_mode',
            'segmented_labelling',
            'json_label',
            )
