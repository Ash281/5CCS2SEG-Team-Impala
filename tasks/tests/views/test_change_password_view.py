"""Tests of the Email Verification view."""
import uuid
from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import NewPasswordMixin
from tasks.models import User

class ChangePasswordTestCase(TestCase):
    """Tests of the change password view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.user.email_verification_token = str(uuid.uuid4())
        self.user.save()
        self.user.refresh_from_db()
        self.url = reverse('new_password', args=[self.user.email_verification_token])
        self.form_input = {
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }
        
    def test_change_password_url_with_valid_token(self):
        self.assertEqual(self.url, f'/new_password/{self.user.email_verification_token}/')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewPasswordMixin))

    def test_change_password_url_with_different_token(self):
        different_token_url = f'/new_password/{str(uuid.uuid4())}/'
        self.assertNotEqual(self.url, different_token_url)
        response = self.client.get(different_token_url, follow=True)
        redirect_url = reverse('email_verify')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'email_verify.html')

    def test_succesful_password_change(self):
        response = self.client.post(self.url, self.form_input, follow=True)

        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user.password)
        
        self.assertTrue(is_password_correct)

    def test_invalid_form(self):
        self.form_input['password_confirmation'] = 'WRONG_PASSWORD'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewPasswordMixin))
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        messages = list(response.context['messages'])
        self.assertEqual(messages[0].tags, "danger")


    