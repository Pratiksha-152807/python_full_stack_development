from django.test import TestCase
import re

from django.core import mail
from django.test import TestCase, override_settings
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
            email='student@example.com',
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

    def test_login_links_to_registration_and_password_reset(self):
        response = self.client.get('/login/')

        self.assertContains(response, 'Create a new account')
        self.assertContains(response, 'Forgot your password?')

    def test_registration_creates_user_and_redirects_to_login(self):
        response = self.client.post('/register/', {
            'username': 'new-student',
            'email': 'new-student@example.com',
            'password1': 'different-password-456',
            'password2': 'different-password-456',
        }, follow=True)

        self.assertRedirects(response, '/login/')
        self.assertContains(response, 'Your account has been created.')
        user = User.objects.get(username='new-student')
        self.assertEqual(user.email, 'new-student@example.com')
        self.assertTrue(user.check_password('different-password-456'))

    def test_registration_rejects_duplicate_username(self):
        response = self.client.post('/register/', {
            'username': self.user.username,
            'email': 'another@example.com',
            'password1': 'different-password-456',
            'password2': 'different-password-456',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        self.assertEqual(User.objects.count(), 1)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_email_link_changes_password(self):
        response = self.client.post('/password-reset/', {
            'email': self.user.email,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'If an account exists')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your Student services password', mail.outbox[0].subject)

        reset_link = re.search(
            r'/reset/([^/]+)/([^/\s]+)/',
            mail.outbox[0].body,
        )
        self.assertIsNotNone(reset_link)
        uidb64, token = reset_link.groups()
        reset_url = f'/reset/{uidb64}/{token}/'
        response = self.client.get(reset_url, follow=True)
        self.assertEqual(response.status_code, 200)
        reset_url = response.redirect_chain[-1][0]

        response = self.client.post(reset_url, {
            'new_password1': 'changed-password-456',
            'new_password2': 'changed-password-456',
        }, follow=True)

        self.assertContains(response, 'Your password has been changed.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('changed-password-456'))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_does_not_disclose_unknown_email(self):
        response = self.client.post('/password-reset/', {
            'email': 'unknown@example.com',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'If an account exists')
        self.assertEqual(len(mail.outbox), 0)

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
