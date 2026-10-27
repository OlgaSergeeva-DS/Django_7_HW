from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from employees.models import EmployeeSkill, Skill

from .models import Workplace

# Create your tests here.
User = get_user_model()


class WorkplaceValidatorTest(TestCase):
    """Тесты валидатора соседних столов (К5)."""

    def setUp(self):
        # 1. Создаем навыки
        self.skill_tester = Skill.objects.create(name="Testing")
        self.skill_dev = Skill.objects.create(name="Backend")

        # 2. Создаем сотрудников
        self.tester = User.objects.create_user(
            username="tester", password="password123"
        )
        self.dev = User.objects.create_user(username="dev", password="password123")

        # 3. Выдаем им навыки
        EmployeeSkill.objects.create(
            employee=self.tester, skill=self.skill_tester, level=5
        )
        EmployeeSkill.objects.create(employee=self.dev, skill=self.skill_dev, level=5)

        # 4. Создаем рабочее место для тестировщика (Стол 2)
        # (Мы используем .save(), а не .full_clean(), чтобы просто создать запись без проверок)
        self.workplace_tester = Workplace.objects.create(
            desk_number="2", employee=self.tester
        )

    def test_validator_blocks_neighbor_developer(self):
        """Разработчик не должен садиться за соседний стол (Стол 1 или 3)."""

        # Пытаемся создать рабочее место для разработчика за Стол 1
        # (Стол 1 соседствует со Столом 2, где сидит тестировщик)
        workplace_dev = Workplace(desk_number="1", employee=self.dev)

        # Мы ожидаем, что метод full_clean() выбросит ошибку ValidationError
        with self.assertRaises(ValidationError):
            workplace_dev.full_clean()

    def test_validator_allows_non_neighbor_desk(self):
        """Разработчик может сесть за стол, который не соседствует с тестировщиком."""

        # Пытаемся посадить разработчика за Стол 5
        # (Стол 5 далеко от Стола 2)
        workplace_dev = Workplace(desk_number="5", employee=self.dev)

        try:
            # Если ошибки нет, этот код выполнится без исключений
            workplace_dev.full_clean()
        except ValidationError:
            self.fail("Валидатор ошибочно заблокировал безопасный стол!")
