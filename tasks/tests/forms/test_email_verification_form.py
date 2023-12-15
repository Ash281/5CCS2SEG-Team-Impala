"""Unit tests of the sign up form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tasks.forms import EmailVerificationForm, SignUpForm
from tasks.models import User

class EmailVeficationTestCase(TestCase):
    """Unit tests of the sign up form."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'username': '@johndoe'
        }

    def test_valid_email_verification_form(self):
        form = EmailVerificationForm(data=self.form_input)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = EmailVerificationForm()
        self.assertIn('username', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = EmailVerificationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = EmailVerificationForm(data=self.form_input)
        form.save()
        user = User.objects.get(username='@johndoe')
        self.assertIsNotNone(user.email_verification_token)
    
    def test_form_save_not_called_when_invalid(self):
        invalid_form_input = {
            'username': 'nonexistentuser'
        }
        form = EmailVerificationForm(data=invalid_form_input)
        if form.is_valid():
            form.save()
        self.assertFalse(form.is_valid())
        self.assertRaises(User.DoesNotExist, User.objects.get, username='nonexistentuser')