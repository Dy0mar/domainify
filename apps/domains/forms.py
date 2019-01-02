# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from domains.models import Domain


class DomainChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DomainChangeForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['name'].widget.attrs['disabled'] = 'disabled'
        for field in self.fields:
            if field in ('date_register', 'date_expire', 'date_last_scan'):
                css_class = 'form-control js-datepicker'
            else:
                css_class = 'form-control'
            self.fields[field].widget.attrs['class'] = css_class

            if field == 'admin':
                self.fields[field].queryset = User.objects.filter(
                    is_superuser=True)
            if field == 'manager':
                self.fields[field].queryset = User.objects.filter(is_staff=True)

    @staticmethod
    def validate_nums(phone):
        max_lenght = 12
        if not phone:
            return None

        try:
            phone = int(phone)
        except (TypeError, ValueError):
            raise ValidationError('Only nums')
        else:
            if len(str(phone)) > max_lenght:
                raise ValidationError('12 or less')
        return phone

    def clean_name(self):
        if self.instance.name:
            return self.instance.name
        return self.cleaned_data['name']

    def clean_telephone(self):
        return self.validate_nums(self.cleaned_data['telephone'])

    def clean_telephone2(self):
        if self.cleaned_data['telephone2']:
            return self.validate_nums(self.cleaned_data['telephone2'])
        else:
            return self.cleaned_data['telephone2']

    def clean_telephone3(self):
        if self.cleaned_data['telephone3']:
            return self.validate_nums(self.cleaned_data['telephone3'])
        else:
            return self.cleaned_data['telephone3']

    class Meta(object):
        model = Domain
        fields = (
            'name', 'manager', 'company_name', 'telephone', 'telephone2',
            'telephone3', 'date_register', 'date_expire', 'admin',
            'pci_scan_name', 'status', 'company_address', 'date_last_scan'
        )


class DomainFilterForm(forms.Form):
    NULL_CHOICES = (
        (None, "---"),
        (1, "Yes"),
        (0, "No")
    )
    STATUS_CHOICE = Domain.CHOICE_STATUS + ((None, "---"),)
    date_input_formats = ['%d.%m.%Y']

    status = forms.NullBooleanField(
        widget=forms.Select(choices=STATUS_CHOICE))
    pci_scan = forms.NullBooleanField(
        widget=forms.Select(choices=NULL_CHOICES))

    managers = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    admins = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    date_request = forms.DateField(input_formats=date_input_formats)

    date_register_from = forms.DateField(input_formats=date_input_formats)
    date_register_till = forms.DateField(input_formats=date_input_formats)

    date_expire_from = forms.DateField(input_formats=date_input_formats)
    date_expire_till = forms.DateField(input_formats=date_input_formats)

    def __init__(self, *args, **kwargs):
        super(DomainFilterForm, self).__init__(*args, **kwargs)
        qs = User.objects.all()
        for field in self.fields:
            self.fields[field].required = False

            if field in ('date_request', 'date_register_from',
                         'date_register_till', 'date_expire_from',
                         'date_expire_till'):
                self.fields[field].widget.attrs['class'] = 'js-datepicker'

            if field == 'managers':
                managers_qs = qs.filter(is_staff=True)
                choices = [[x.pk, x.username] for x in managers_qs]
                choices.append(['None', 'None'])
                self.fields[field].choices = choices

            if field == 'admins':
                admins_qs = qs.filter(is_superuser=True)
                choices = [[x.pk, x.username] for x in admins_qs]
                choices.append(['None', 'None'])
                self.fields[field].choices = choices


class DomainImportForm(forms.Form):
    import_file = forms.FileField()
