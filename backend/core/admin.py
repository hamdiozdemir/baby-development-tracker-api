"""
Admin Site Registerations
"""

from django.contrib import admin
from .models import (CustomUser, Tester, Parent, Child, Comments,
                     Tests, Categories, Instructions, Items,
                     Percentages, Records)

admin.site.register(Tester)
admin.site.register(Parent)
admin.site.register(Child)
admin.site.register(Comments)
admin.site.register(Tests)
admin.site.register(Instructions)
admin.site.register(Percentages)
admin.site.register(Records)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "role"]
    readonly_fields = ['password']


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_filter = ["test"]


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_filter = ["test", "category"]
