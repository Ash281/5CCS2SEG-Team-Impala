from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, CreateTaskForm
from tasks.helpers import login_prohibited
from .models import Task
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    first_three = Task.objects.order_by('due_date')[:3]
    next_three = Task.objects.order_by('due_date')[3:6]

    return render(request, 'dashboard.html', {'user': current_user, 'first_three': first_three, 'next_three': next_three})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

def create_task(request):
    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            form.save()
        
    else:
        form = CreateTaskForm()

    return render(request, 'create_task.html', {'form': form})

def task_list(request):
    sort_by = request.GET.get('sort_by', 'due_date')  

    if sort_by == 'priority':
        tasks = Task.objects.order_by('priority')  
    elif sort_by == 'status':
        tasks = Task.objects.order_by('-status')  # incomplete tasks first
    elif sort_by == 'task_title':
        tasks = Task.objects.order_by('task_title')  
    else:  
        tasks = Task.objects.order_by('due_date')
 
    filter_by = request.GET.get('filter_by', '')  

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if filter_by == 'date_range' and start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        tasks = Task.objects.filter(due_date__range=[start_date, end_date])
    elif filter_by == 'high_priority':
        tasks = Task.objects.filter(priority='HI')  
    elif filter_by == 'med_priority':
        tasks = Task.objects.filter(priority='MD') 
    elif filter_by == 'low_priority':
        tasks = Task.objects.filter(priority='LW') 
    elif filter_by == 'incomp_status':
        tasks = Task.objects.filter(status='NOT_STARTED') 
    elif filter_by == 'comp_status':
        tasks = Task.objects.filter(status='COMPLETED') 

    search = request.GET.get('search', '')  

    if search:
        tasks = Task.objects.filter(task_title__icontains=search)
    

    return render(request, 'task_list.html', {'tasks': tasks, 'sort_by': sort_by, 'filter_by': filter_by})

def task_detail(request, task_title):
    task = get_object_or_404(Task, pk=task_title)
    return render(request, 'task_detail.html', {'task': task})


def edit_task(request, task_title):
    task = get_object_or_404(Task, task_title=task_title)
    if request.method == 'POST':
        form = CreateTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')  
    else:
        form = CreateTaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})


@require_POST
def mark_task_complete(request, task_title):
    task = get_object_or_404(Task, task_title=task_title)
    task.status = 'COMPLETED'
    task.save()
    return redirect('task_list') 

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


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

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