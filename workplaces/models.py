from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from employees.models import EmployeeSkill, Skill


# Create your models here.
class Workplace(models.Model):
    """Модель рабочего места."""

    desk_number = models.CharField(
        max_length=20,
        unique=True,  # Номера столов не должны повторяться
        verbose_name="Номер стола",
    )
    description = models.TextField(
        verbose_name="Дополнительная информация",
        blank=True,
        help_text="Например: 'У окна', 'Рядом с принтером'",
    )
    # Связь "один к одному" с моделью пользователя (сотрудника)
    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Ссылаемся на нашу кастомную модель
        on_delete=models.SET_NULL,  # Если сотрудника удалят, рабочее место останется, но станет свободным
        null=True,
        blank=True,
        verbose_name="Закреплённый сотрудник",
        related_name="workplace",  # Позволит из сотрудника получить его рабочее место: user.workplace
    )

    def clean(self):
        super().clean()

        # Если сотрудник не привязан, проверять нечего
        if not self.employee:
            return

        # Получаем навыки текущего сотрудника
        employee_skills = set(
            EmployeeSkill.objects.filter(employee=self.employee).values_list(
                "skill__name", flat=True
            )
        )

        # Определяем, кто наш сотрудник: тестировщик или разработчик
        is_tester = "Testing" in employee_skills
        is_developer = any(
            skill in employee_skills for skill in ["Frontend", "Backend"]
        )

        if not (is_tester or is_developer):
            return  # Если он не тестировщик и не разработчик, проверка не нужна

        # Находим соседние столы
        try:
            desk_num = int(self.desk_number)
        except (ValueError, TypeError):
            return  # Если номер не числовой, пропускаем

        neighbor_desks = [str(desk_num - 1), str(desk_num + 1)]

        # Ищем, кто сидит за соседними столами
        neighbors = Workplace.objects.filter(desk_number__in=neighbor_desks).exclude(
            pk=self.pk
        )

        for neighbor in neighbors:
            if not neighbor.employee:
                continue

            neighbor_skills = set(
                EmployeeSkill.objects.filter(employee=neighbor.employee).values_list(
                    "skill__name", flat=True
                )
            )

            neighbor_is_tester = "Testing" in neighbor_skills
            neighbor_is_developer = any(
                skill in neighbor_skills for skill in ["Frontend", "Backend"]
            )

            # Если один тестировщик, а другой разработчик — ошибка
            if (is_tester and neighbor_is_developer) or (
                is_developer and neighbor_is_tester
            ):
                raise ValidationError(
                    "Тестировщики и разработчики не могут сидеть за соседними столами. "
                    f"За столом №{neighbor.desk_number} сидит сотрудник с другим профилем."
                )

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"

    def __str__(self):
        return f"Стол №{self.desk_number}"
