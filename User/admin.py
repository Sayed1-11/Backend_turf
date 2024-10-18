from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserModel

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
class UserAdmin(BaseUserAdmin):
    exclude = ('user_registered_at',)
    list_display = ['id', 'phone_number', 'name','role','otp', 'is_staff']
    search_fields = ('phone_number', 'name','role', 'email')
    ordering = ['phone_number']
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('name', 'email', 'profile_image','latitude','longitude', 'birthdate', 'gender', 'address','otp','otp_expiry','max_otp_try','otp_max_out')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
        ('Important dates', {'fields': ('last_login', 'user_registered_at')}),
    )
    readonly_fields = ('last_login', 'user_registered_at')

# Register the UserAdmin with the UserModel
admin.site.register(UserModel, UserAdmin)