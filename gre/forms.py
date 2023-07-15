from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from .models import Word, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class WordForm(ModelForm):
    
    class Meta:
        model = Word
        fields = '__all__'
        exclude = ('learner', )