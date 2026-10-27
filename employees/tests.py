from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Create your tests here.
User = get_user_model()


class BaseViewTest(TestCase):
    """Базовый класс для создания тестовых данных."""

    def setUp(self):
        # Создаем обычного сотрудника
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="password123",
            first_name="Иван",
            last_name="Иванов",
        )
        # Создаем суперпользователя (для проверки прав)
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password123"
        )


class HomeViewTest(BaseViewTest):
    """Тесты для главной страницы (К1)."""

    def test_home_url_exists(self):
        """Проверка доступности главной страницы."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_context_contains_total_employees(self):
        """Проверка контекста: общее количество сотрудников."""
        response = self.client.get(reverse("home"))
        # У нас создано 2 пользователя (testuser1 и admin)
        self.assertEqual(response.context["total_employees"], 2)

    def test_home_context_contains_latest_employees(self):
        """Проверка контекста: вывод 4 последних сотрудников."""
        # Просто убедимся, что ключ 'employees' есть в контексте
        response = self.client.get(reverse("home"))
        self.assertIn("employees", response.context)


class EmployeeListViewTest(BaseViewTest):
    """Тесты для списка сотрудников (К2)."""

    def test_employee_list_url_exists(self):
        """Проверка доступности страницы списка."""
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)

    def test_employee_list_context_contains_page_obj(self):
        """Проверка контекста: наличие объекта пагинации."""
        response = self.client.get(reverse("employee_list"))
        # Так как мы используем Paginator, в контексте должен быть page_obj
        self.assertIn("page_obj", response.context)

        # Проверим, что в page_obj лежат наши сотрудники
        self.assertEqual(len(response.context["page_obj"]), 2)


class EmployeeDetailViewTest(BaseViewTest):
    """Тесты прав доступа к подробной карточке (К3, К4)."""

    def test_employee_detail_url_redirects_anonymous(self):
        """Анонимный пользователь должен перенаправляться на логин."""
        url = reverse("employee_detail", args=[self.user1.pk])
        response = self.client.get(url)
        # Код 302 означает редирект (перенаправление)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что редирект идет на страницу логина
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_employee_detail_url_accessible_for_logged_in(self):
        """Авторизованный пользователь должен видеть страницу."""
        # Логиним пользователя
        self.client.login(username="testuser1", password="password123")

        url = reverse("employee_detail", args=[self.user1.pk])
        response = self.client.get(url)

        # Теперь код ответа должен быть 200 (ОК)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в контексте правильный сотрудник
        self.assertEqual(response.context["employee"], self.user1)
