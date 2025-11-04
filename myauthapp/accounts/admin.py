from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ('username', 'email', 'is_active', 'email_verified', 'date_joined')
    list_filter = ('is_active', 'email_verified', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'profile_picture', 'city', 'email_verified')
        }),
    )
    readonly_fields = ('email_verified',)

admin.site.register(CustomUser, CustomUserAdmin)