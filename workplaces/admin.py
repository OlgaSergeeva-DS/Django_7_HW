from django.contrib import admin

from .models import Workplace


# Register your models here.
@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ("desk_number", "employee", "description")
    list_filter = ("employee",)
    search_fields = ("desk_number", "employee__last_name")
