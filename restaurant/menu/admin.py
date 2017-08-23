from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'chef']
    class Meta:
        model=models.Food


admin.site.register(models.Review)
admin.site.register(models.Order)
