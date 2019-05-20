# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db.models import Q

from users.models import User
from domains.models import Domain, ActionLog


class DomainChangeForm(forms.ModelForm):
    perm = Permission.objects.filter(
        codename='can_manage_domain_registrar').first()

    admin_registrar = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.filter(Q(groups__permissions=perm)).distinct(),
    )

    admin_whois = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.filter(Q(groups__permissions=perm)).distinct(),
    )

    notify_admin_registrar = forms.BooleanField(required=False)
    notify_admin_whois = forms.BooleanField(required=False)

    perm = Permission.objects.filter(codename='can_edit_site').first()
    admin_editor = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.filter(Q(groups__permissions=perm)).distinct()
    )

    notify_admin_editor = forms.BooleanField(
        required=False
    )
    editor_method = forms.ChoiceField(
        choices=(('text', 'Текстом'), ('image', 'Картинкой')),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.allow_change_name = kwargs.pop('allow_change_name', False)
        self.user = kwargs.pop('user', None)
        super(DomainChangeForm, self).__init__(*args, **kwargs)

        if self.instance.pk and not self.allow_change_name:
            self.fields['name'].widget.attrs['readonly'] = 'readonly'

        qs = User.objects.all()
        self.fields['admin'].queryset = qs.filter(is_superuser=True)
        self.fields['manager'].queryset = qs.filter(is_staff=True)

        # set domain statuses
        if not self.user.is_superuser:
            choices = [('CURRENT', '---')] + [
                x for x in Domain.CHOICE_STATUS if x[0].startswith('REQUIRES_')
            ]
            self.fields['status'].choices = choices

        epmty_css = (
            'notify_admin_registrar', 'admin_registrar', 'notify_admin_editor',
            'admin_editor', 'notify_admin_whois', 'admin_whois'
        )
        for field in self.fields:
            if field in epmty_css:
                continue

            if field in ('date_register', 'date_expire', 'date_last_scan'):
                css_class = 'form-control js-datepicker'
            else:
                css_class = 'form-control'

            self.fields[field].widget.attrs['class'] = css_class

    @staticmethod
    def validate_nums(phone):
        max_length = 12
        if not phone:
            return None

        try:
            phone = int(phone)
        except (TypeError, ValueError):
            raise ValidationError('Only nums')
        else:
            if len(str(phone)) > max_length:
                raise ValidationError('12 or less')
        return phone

    def clean_status(self):
        value = self.cleaned_data['status']

        # по-умолчанию сразу в active
        if not self.instance.pk:
            return Domain.ACTIVE

        # если ничего не выбирали
        if value == 'CURRENT':
            return self.instance.status

        return value

    def clean_name(self):
        if self.instance.name and not self.allow_change_name:
            return self.instance.name

        # split domain(. and -) and check it isalnum
        domain = self.cleaned_data['name']
        result = [x.isalnum() for x in re.split(r'\.|\-', domain)]
        if all(result):
            return self.cleaned_data['name']
        raise ValidationError('Only chars, nums and point')

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

    def clean_admin_registrar(self):
        notify = self.cleaned_data['notify_admin_registrar']
        value = self.cleaned_data['admin_registrar']

        if notify and not value:
            raise forms.ValidationError(
                'Выберите админа, которого надо оповестить о смене редиректа'
            )
        return value

    def clean_admin_editor(self):
        notify = self.cleaned_data['notify_admin_editor']
        value = self.cleaned_data['admin_editor']

        if notify and not value:
            raise forms.ValidationError(
                'Выберите админа, которого надо '
                'оповестить о редакировании информации на сайте '
            )
        return value

    def save(self, commit=True):
        domain = self.instance
        if domain.pk:
            action = ActionLog.EDIT_DOMAIN
            data = {}
            old_domain = self.initial
            # list
            for field in self.changed_data:
                old = old_domain.get(field, '')
                new = self.cleaned_data[field]

                # list of users
                if field in ('admin_registrar', 'admin_editor', 'admin_whois'):
                    new = ', '.join([x.username for x in new])

                elif field in ('manager', 'admin'):
                    if old:
                        try:
                            old = User.objects.get(pk=old)
                            old = old.username
                        except User.DoesNotExist:
                            pass
                    new = new.username if new else ''

                data['old_' + field] = old
                data[field] = new
        else:
            action = ActionLog.ADD_DOMAIN
            data = None

        domain.save()
        log = ActionLog.objects.create(
            action=action,
            user=self.user,
            data=data,
            domain=domain
        )

        if self.user == domain.manager:
            log.is_read = True
            log.save()

        return domain

    class Meta(object):
        model = Domain
        fields = (
            'name', 'manager', 'company_name', 'telephone', 'telephone2',
            'telephone3', 'email', 'email2', 'email3',
            'redirect', 'date_register', 'date_expire', 'admin',
            'pci_scan_name', 'status', 'company_address', 'date_last_scan',
            'notify_admin_registrar', 'notify_admin_editor', 'admin_editor',
            'admin_registrar', 'redirect_phone', 'notify_admin_whois'
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
    alexa_status = forms.NullBooleanField(
        widget=forms.Select(choices=Domain.ALEXA_STATUSES))
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


class DomainAlexaForm(forms.ModelForm):
    perm = Permission.objects.filter(
        codename='can_manage_alexa_traffic').first()

    executors = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=User.objects.filter(
            Q(groups__permissions=perm)).distinct()
    )
    cancel = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.initiator = kwargs.pop('initiator', None)
        self.user_executors = kwargs.pop('user_executors', None)

        super(DomainAlexaForm, self).__init__(*args, **kwargs)
        # set required
        self.fields['alexa_comment'].required = True

        # Исполнителей задавать только на первом шаге
        qs = self.fields['executors'].choices.queryset
        qs = qs.exclude(username=self.user.username)
        self.fields['executors'].queryset = qs

        if self.initiator:
            self.fields['alexa_comment'].widget.attrs = {'readonly': 'readonly'}
            del self.fields['executors']

        # set statuses
        start = 0
        end = 2
        factor = 0
        choices = tuple()
        if self.instance.alexa == Domain.ALEXA_REQUIRES_ON:
            factor = 1
        if self.instance.alexa == Domain.ALEXA_ON:
            factor = 2
        if self.instance.alexa == Domain.ALEXA_REQUIRES_OFF:
            choices = (Domain.ALEXA_STATUSES[3], Domain.ALEXA_STATUSES[0])

        start += factor
        end += factor
        choices = choices or Domain.ALEXA_STATUSES[start:end]
        self.fields['alexa'].choices = choices

        # set css classes
        for field in self.fields:
            if field == 'executors':
                css_class = 'form-check-label list-unstyled'
            elif field == 'cancel':
                css_class = 'hide'
            else:
                css_class = 'form-control'

            self.fields[field].widget.attrs['class'] = css_class

    def clean_alexa(self):
        cancel = self.cleaned_data.get('cancel')

        if cancel and self.user == self.initiator:
            return Domain.ALEXA_OFF

        value = self.cleaned_data.get('alexa')
        curr_alexa = self.instance.alexa

        if value == curr_alexa and value == Domain.ALEXA_OFF:
            raise forms.ValidationError('Статус уже выключен')

        if value == curr_alexa:
            return value

        if self.user == self.initiator and value not in (
                Domain.ALEXA_REQUIRES_ON, Domain.ALEXA_REQUIRES_OFF
        ):
            raise forms.ValidationError(
                'Статус {} доступен только исполнителю'.format(value))

        if self.user in self.user_executors and value not in (
                Domain.ALEXA_ON, Domain.ALEXA_OFF
        ):
            raise forms.ValidationError(
                'Статус {} доступен только инициатору'.format(value))

        if value == Domain.ALEXA_REQUIRES_ON:
            if curr_alexa == Domain.ALEXA_OFF:
                return value
            else:
                raise forms.ValidationError(
                    'Запросить подтверждение на включение'
                    ' можно только из статуса OFF')

        if value == Domain.ALEXA_ON:
            if curr_alexa == Domain.ALEXA_REQUIRES_ON:
                return value
            else:
                raise forms.ValidationError(
                    'Включить статус ON можно только после подтверждения')

        if value == Domain.ALEXA_REQUIRES_OFF:
            if curr_alexa == Domain.ALEXA_ON:
                return value
            else:
                raise forms.ValidationError(
                    'Запросить подтверждение на выключение'
                    ' можно только из статуса ON')

        if value == Domain.ALEXA_OFF:
            if curr_alexa == Domain.ALEXA_REQUIRES_OFF:
                return value
            else:
                raise forms.ValidationError(
                    'Включить статус OFF можно только после подтверждения')

        raise forms.ValidationError(
            'Что-то пошло совсем не так. Обратитесь к программисту')

    def clean_executors(self):
        cancel = self.cleaned_data.get('cancel')
        alexa = self.cleaned_data.get('alexa')
        users = self.cleaned_data.get('executors')
        if alexa != Domain.ALEXA_OFF and not cancel:
            if not users:
                raise forms.ValidationError(
                    'Выберите хотя бы одного исполнителя')
            return users

    def save(self, commit=True):
        data = {
            'status': self.instance.alexa,
            'comment': self.instance.alexa_comment,
            'user': self.user.username,
        }
        if self.cleaned_data.get('cancel'):
            data['cancel'] = 'CANCEL'

        ActionLog.objects.create(
            action=ActionLog.ALEXA,
            user=self.user,
            data=data,
            domain=self.instance
        )

        self.instance.save()
        return self.instance

    class Meta(object):
        model = Domain
        fields = (
            'cancel', 'alexa', 'alexa_comment', 'executors'
        )


class DomainImportForm(forms.Form):
    import_file = forms.FileField()
