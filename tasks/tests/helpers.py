from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from django.core.mail import send_mail
from task_manager import settings

def reverse_with_next(url_name, next_url):
    """Extended version of reverse to generate URLs with redirects"""
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

def send_email(email, token):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    settings.EMAIL_HOST = 'smtp.gmail.com'
    settings.EMAIL_HOST_USER = 'impalaseg@gmail.com'
    settings.EMAIL_HOST_PASSWORD = 'rspuxroqkvlsinmw'
    settings.EMAIL_PORT = 587
    settings.EMAIL_USE_TLS = True

    subject = 'Reset Password Link'
    body = f"Hi there, \nThis is your link to reset your password: http://127.0.0.1:8000/new_password/{token}/"
    send_mail(subject, body, settings.EMAIL_HOST_USER, [email])



class LogInTester:
    """Class support login in tests."""
 
    def _is_logged_in(self):
        """Returns True if a user is logged in.  False otherwise."""

        return '_auth_user_id' in self.client.session.keys()

class MenuTesterMixin(AssertHTMLMixin):
    """Class to extend tests with tools to check the presents of menu items."""

    menu_urls = [
        reverse('password'), reverse('profile'), reverse('log_out')
    ]

    def assert_menu(self, response):
        """Check that menu is present."""

        for url in self.menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass

    def assert_no_menu(self, response):
        """Check that no menu is present."""
        
        for url in self.menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')