# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserChangeForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field in ('is_staff', 'is_superuser'):
                self.fields[field].widget.attrs['class'] = 'form-check-label'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'groups', 'password1', 'password2',
                  'is_staff', 'is_superuser', 'pidgin')


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super(UserForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field in ('is_staff', 'is_superuser'):
                self.fields[field].widget.attrs['class'] = 'form-check-label'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_is_staff(self):
        value = self.cleaned_data['is_staff']
        if self.instance.is_superuser:
            return value

        if self.instance.is_staff and value:
            return value

        raise forms.ValidationError(
            'Вы не можете изменить свой стаус, попросите админа')

    def clean_is_superuser(self):
        value = self.cleaned_data['is_superuser']
        u = self.instance

        if not u.is_superuser:
            if value:
                raise forms.ValidationError(
                    'Вы не можете назначить себя админом, '
                    'попросите другого админа')
            return value

        if u.is_superuser and u == self.current_user:
            if not value:
                raise forms.ValidationError(
                    'Вы не можете снять с себя админку, '
                    'попросите другого админа')
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'groups', 'pidgin',
                  'is_staff', 'is_superuser')
