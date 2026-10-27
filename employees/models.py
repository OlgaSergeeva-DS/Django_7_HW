from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from jodit.fields import RichTextField


# Create your models here.
class User(AbstractUser):
    """Расширенная модель пользователя (сотрудника)."""

    # Поле для выбора пола. Используем choices для ограничения вариантов.
    GENDER_CHOICES = (
        ("М", "Мужской"),
        ("Ж", "Женский"),
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Пол",
        blank=True,  # Разрешаем оставлять поле пустым
    )
    # Отчество (при наличии). Может быть пустым.
    patronymic = models.CharField(
        max_length=150,
        verbose_name="Отчество",
        blank=True,  # Разрешаем оставлять поле пустым
    )
    # Биография сотрудника:
    bio = RichTextField(
        verbose_name="Биография",
        blank=True,
        help_text="Краткая информация о сотруднике, его опыте и т.д.",
        config_name="default",  # Используем настройки по умолчанию
    )
    # Добавляем дату приема на работу
    hire_date = models.DateField(
        verbose_name="Дата приёма на работу",
        null=True,
        blank=True,
        help_text="Укажите дату, когда сотрудник был принят",
    )

    @property
    def experience_days(self):
        """Возвращает стаж работы в днях."""
        if not self.hire_date:
            return 0
        today = timezone.now().date()
        delta = today - self.hire_date
        return delta.days

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        permissions = [
            ("can_move_employee", "Может перемещать сотрудников между столами"),
        ]

    # Этот метод определяет, как объект будет выглядеть в админке и консоли.
    def __str__(self):
        # Показываем Фамилию Имя, а если их нет — логин (username)
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.username


""" 
Что здесь происходит:
AbstractUser — это встроенная модель Django, которая уже содержит поля:
- для логина, пароля, имени, фамилии, email и прав доступа. 
Мы наследуемся от неё и добавляем свои поля: gender (пол) и patronymic (отчество). 
Поля first_name (имя) и last_name (фамилия) у нас уже есть благодаря AbstractUser.

choices — это способ ограничить значения поля. В админке вместо текстового поля появится выпадающий список .

__str__ — «магический» метод Python, который возвращает строковое представление объекта. 
В админке сотрудники будут отображаться как «Фамилия Имя», а не как «User object (1)».
"""


class Skill(models.Model):
    """Модель для хранения названия навыка (Python, React и т.д.)."""

    name = models.CharField(
        max_length=100,
        verbose_name="Название навыка",
        unique=True,  # Названия не должны повторяться
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    """Промежуточная модель, связывающая сотрудника и навык с уровнем владения."""

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Если удалить сотрудника, удалятся и его навыки
        verbose_name="Сотрудник",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        verbose_name="Навык",
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Уровень владения (1-10)",
        help_text="Введите число от 1 до 10",
    )

    class Meta:
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"
        # Гарантируем, что у одного сотрудника не будет двух записей об одном навыке
        unique_together = ("employee", "skill")

    def __str__(self):
        return f"{self.employee} - {self.skill} ({self.level})"


class EmployeeImage(models.Model):
    """Галерея изображений сотрудника."""

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="images",  # Позволит получать все фото через user.images.all()
        verbose_name="Сотрудник",
    )
    image = models.ImageField(upload_to="employees/", verbose_name="Фотография")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер")

    class Meta:
        verbose_name = "Изображение сотрудника"
        verbose_name_plural = "Изображения сотрудников"
        ordering = ["order"]  # Сортировка по номеру по умолчанию

    def __str__(self):
        return f"Фото {self.employee} - №{self.order}"
