"""Tests of the Email Verification view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import EmailVerificationForm
from tasks.models import User
from tasks.tests.helpers import send_email

class EmailVerificationTestCase(TestCase):
    """Tests of the email verification view."""

    fixtures = ['tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('email_verify')
        self.user = User.objects.get(username='@petrapickles')
        self.second_user = User.objects.get(username='@janedoe')
        self.form_input = {"username":"@petrapickles"}

    def test_email_verify_url(self):
        self.assertEqual(self.url,'/email_verify/')

    def test_get_email_verification(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EmailVerificationForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_email_verification(self):
        self.form_input['username'] = 'BAD_USERNAME'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EmailVerificationForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertIsNone(self.user.email_verification_token)

    def test_succesful_email_verification(self):
        response = self.client.post(self.url, self.form_input)
        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verification_token)

        send_email(self.user.email, self.user.email_verification_token)


    def test_user_receives_token(self):
        response = self.client.post(self.url, self.form_input)
        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(form.is_valid)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verification_token)

    def test_token_is_unique(self):
        response = self.client.post(self.url, self.form_input)
        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(form.is_valid)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verification_token)

        self.form_input['username'] = self.second_user.username
        response = self.client.post(self.url, self.form_input)
        self.assertTemplateUsed(response, 'email_verify.html')
        form = response.context['form']
        self.assertTrue(form.is_valid)
        
        self.second_user.refresh_from_db()
        self.assertIsNotNone(self.second_user.email_verification_token)

        self.assertNotEquals(self.user.email_verification_token, self.second_user.email_verification_token)



