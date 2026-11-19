from django.test import TestCase
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
