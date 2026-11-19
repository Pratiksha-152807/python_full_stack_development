from django.test import TestCase
from django.contrib.auth.models import User
from .models import Student_table


class StudentFormViewTests(TestCase):
    def test_student_form_page_renders(self):
        response = self.client.get('/add_form/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student registration')

    def test_duplicate_registration_number_is_rejected(self):
        Student_table.objects.create(reg_no=123, name='Existing student')

        response = self.client.post('/add_form/', {
            'reg_no1': 123,
            'name1': 'New student',
            'email1': 'new@example.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already registered')
        self.assertEqual(Student_table.objects.count(), 1)

    def test_valid_submission_saves_student(self):
        response = self.client.post('/add_form/', {
            'reg_no1': 456,
            'name1': 'New student',
            'email1': 'new@example.com',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student registered successfully.')
        self.assertTrue(Student_table.objects.filter(reg_no=456).exists())

    def test_invalid_submission_redisplays_field_errors(self):
        response = self.client.post('/add_form/', {
            'reg_no1': 'not-a-number',
            'name1': '',
            'email1': 'not-an-email',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(response, 'Enter a valid email address.')


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student-test',
            password='test-password-123',
        )

    def test_login_page_renders_accessible_fields(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'for="username"')
        self.assertContains(response, 'for="password"')

    def test_invalid_login_shows_error(self):
        response = self.client.post('/login/', {
            'username': self.user.username,
            'password': 'incorrect-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_login_opens_dashboard(self):
        response = self.client.post('/login/', {
            'username': self.user.username,
            'password': 'test-password-123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, student-test')
        self.assertContains(response, 'Sign out')

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')

        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_logout_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post('/logout/', follow=True)

        self.assertRedirects(response, '/login/')
        self.assertRedirects(self.client.get('/dashboard/'), '/login/?next=/dashboard/')
