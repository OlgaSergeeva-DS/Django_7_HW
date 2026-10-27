from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmployeeImage, EmployeeSkill, Skill, User


# 1. СНАЧАЛА создаем Inline-класс для галереи (он должен быть выше, чем его использование)
class EmployeeImageInline(admin.TabularInline):
    model = EmployeeImage
    extra = 1  # Количество пустых форм для добавления новых фото
    fields = ("image", "order")


# 2. Теперь настраиваем саму модель User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения нашей кастомной модели User в админке."""

    # Добавляем встроенную галерею прямо в карточку сотрудника
    inlines = [EmployeeImageInline]

    # 3. Форма РЕДАКТИРОВАНИЯ существующего сотрудника
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("gender", "patronymic", "bio", "hire_date")},
        ),
    )

    # 4. Форма СОЗДАНИЯ нового сотрудника
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "patronymic",
                    "gender",
                    "bio",
                    "hire_date",
                ),
            },
        ),
    )

    # 5. Что показывать в общем списке сотрудников
    list_display = (
        "username",
        "last_name",
        "first_name",
        "gender",
        "hire_date",
        "is_staff",
    )


# 6. Регистрация остальных моделей
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ("employee", "skill", "level")
    list_filter = ("skill", "level")
    search_fields = ("employee__username", "employee__last_name", "skill__name")


@admin.register(EmployeeImage)
class EmployeeImageAdmin(admin.ModelAdmin):
    list_display = ("employee", "image", "order")
