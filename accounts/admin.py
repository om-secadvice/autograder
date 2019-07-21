from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            perm_fields = ()
        
        fieldsets = (
            (None, {'fields': ('email', 'password')}),
            (_('Personal info'), {'fields': ('name','roll_number')}),
            (_('Permissions'), {'fields': perm_fields}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

        return fieldsets

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','roll_number','email', 'password1', 'password2'),
        }),
    )
    
    list_display = ('email', 'name', 'is_staff','is_superuser')
    search_fields = ('email', 'name')
    ordering = ('email',)

