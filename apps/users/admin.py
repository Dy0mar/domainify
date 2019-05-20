# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import Group

from users.group_users_form import GroupAdminForm
from users.models import User


admin.site.register(User)
admin.site.unregister(Group)


# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
