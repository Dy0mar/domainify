# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserChangeForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance')
        if instance:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        for field in self.fields:
            if field in ('is_staff', 'is_superuser'):
                self.fields[field].widget.attrs['class'] = 'form-check-label'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'is_staff', 'is_superuser')


class ProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
