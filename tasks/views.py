import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, NewPasswordMixin, PasswordForm, EmailVerificationForm, UserForm, SignUpForm
from tasks.helpers import login_prohibited
from .models import User

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""


        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')

class EmailVerification(LoginProhibitedMixin, View):
    def get(self, request):
        """Display email_verify template."""
        return self.render()
    
    def post(self, request):
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            
            user = User.objects.get(username=form.get_username())
            token = str(uuid.uuid4())
            self.send_email_verification(user.email, token)

            user.email_verification_token = token
            user.save()
            messages.add_message(request, messages.SUCCESS, "We have sent you an email please check your inbox!")
        else:
            messages.add_message(request, messages.ERROR, "User not found please check your details again")

        return self.render()
    
    
    def send_email_verification(self, email, token):
        subject = 'Reset Password Link'
        body = f"Hi there, \nThis is your link to reset your password: http://127.0.0.1:8000/new_password/{token}/"
        send_mail(subject, body, settings.EMAIL_HOST_USER, [email])

    def render(self):
        """Render email_verify template with blank log in form."""

        form = EmailVerificationForm()
        return render(self.request, 'email_verify.html', {'form': form})
    

class ChangePassword(FormView):
    template_name = 'new_password.html'
    form_class = NewPasswordMixin

    def validate_token(self, token):
        try:
            user = User.objects.filter(email_verification_token=uuid.UUID(str(token))).first()
            return user
        except User.DoesNotExist:
            return None

    def get(self, *args, **kwargs):
        token = kwargs.get('token')
        user = self.validate_token(token)

        if user:
            return render(self.request,'new_password.html', {'token': token, 'form' : NewPasswordMixin()})
        else:
            messages.add_message(self.request, messages.ERROR, "User not found")
            return render(self.request, 'home.html')

    def post(self, request, **kwargs):
        token = kwargs.get('token')
        user = self.validate_token(token)

        form = NewPasswordMixin(request.POST)

        if form.is_valid():
            print("Form is valid")
            form.save(user)
            return redirect(self.get_success_url())
        else:
            messages.add_message(self.request, messages.ERROR, "Password Invalid!")
            return render(self.request,'new_password.html', {'token': token, 'form' : NewPasswordMixin()})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('log_in')

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""
        print(self.request.user)
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)