from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class CustomerInline(admin.StackedInline):
    model = models.Customer
    can_delete = False
    verbose_name_plural = 'customer'

class StaffInline(admin.StackedInline):
    model = models.Staff
    can_delete = False
    verbose_name_plural = 'staff'

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,StaffInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# @admin.register(models.Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['user_type', 'is_approved']
#     class Meta:
#         model=models.Customer

# @admin.register(models.Staff)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['user_type', 'is_approved']
#     class Meta:
#         model=models.Staff

#admin.site.register(models.Review)
