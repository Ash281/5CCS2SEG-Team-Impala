import datetime
import uuid
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse

from tasks.forms import LogInForm, PasswordForm, SearchTaskForm, UserForm, SignUpForm, CreateTeamForm
from tasks.helpers import login_prohibited
from tasks.models import User, Team

from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, CreateTaskForm
from tasks.helpers import login_prohibited
from .models import Task
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date

from tasks.forms import LogInForm, NewPasswordMixin, PasswordForm, EmailVerificationForm, UserForm, SignUpForm, InviteMemberForm, FilterPriorityForm, FilterDateRangeForm, SearchTaskForm
from tasks.helpers import login_prohibited
from .models import User

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    user_teams = current_user.teams.all()
    tasks = Task.objects.filter(assignees=current_user.id)
    todo_tasks_count = 0
    in_progress = 0
    complete_tasks = 0
    for task in tasks:
        if task.status == "TODO":
            todo_tasks_count += 1
        if task.status =="IN_PROGRESS":
            in_progress += 1
        if task.status =="DONE":
            complete_tasks += 1

    return render(request, 'dashboard.html', {'user': current_user, 'user_teams': user_teams,'to_do_tasks':todo_tasks_count,'in_progress' : in_progress, 'done' : complete_tasks})

def filter_function(request):
    
    priority_form = FilterPriorityForm(request.GET)
    date_form = FilterDateRangeForm(request.GET)
    search_form = SearchTaskForm(request.GET)
    priority_choices = {
        'high_priority': 'HI',
        'med_priority': 'MD',
        'low_priority': 'LW',
    }
    priority_filter = request.GET.get('filter_by_priority')
    if priority_filter:
        priority = priority_choices[priority_filter]
    else:
        priority = None
    start_date_filter = request.GET.get('start_date')
    end_date_filter = request.GET.get('end_date')
    if start_date_filter:
        start_date = parse_date(start_date_filter)
    else:
        start_date = None
    if end_date_filter:
        end_date = parse_date(end_date_filter)
    else:
        end_date = None

    search_term = request.GET.get('search')
    if search_term:
        search = search_term
    else:
        search = None
    # You can add more context data as needed
    context = {
        'priority_form' : priority_form,
        'date_form' : date_form,
        'search_form' : search_form,
        'priority' : priority,
        'start_date' : start_date,
        'end_date' : end_date,
        'search' : search
        # Add more context data here
    }
    return context

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class MyTeamsView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        user_teams = current_user.teams.all()
        tasks = Task.objects.filter(assignees=current_user.id)
        

        return render(request, 'my_teams.html', {'user_teams': user_teams,'user_tasks' : tasks})

class MyTasksView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        tasks = Task.objects.filter(assignees=current_user.id)
        user_teams = current_user.teams.all()
        context = (
            {'user_teams': user_teams,
             'user_tasks': tasks}
            )
        add_file = filter_function(request)
        context.update(add_file)

        # Add more context data here
    

        return render(request, 'my_tasks.html', context)
    #        return render(request, 'my_tasks.html', {'user_teams': user_teams, 'user_tasks': tasks})



class TaskDetailsView(LoginRequiredMixin, View):
    def get(self, request, task_title):
        task = get_object_or_404(Task, pk=task_title)
        
        return render(request, 'task_detail.html', {'task': task})

class EditTaskView(LoginRequiredMixin, View):
    template_name = "edit_task.html"

    def get(self, request, task_title):
        task, team = self.get_task_and_team(task_title)
        form = CreateTaskForm(team_id=team.id, instance=task)
        return render(request, self.template_name, {'form': form, 'task': task, 'members':team.members.all(), 'id': team.id})

    def post(self, request, task_title):
        task, team = self.get_task_and_team(task_title)
        form = CreateTaskForm(request.POST, team_id=team.id, instance=task)
        if form.is_valid():
            form.save()
            return redirect('team_dashboard', id=task.team.id)
        return render(request, self.template_name, {'form': form, 'task': task, 'members':team.members.all(), 'id': team.id})
    
    def get_task_and_team(self, task_title):
        task = get_object_or_404(Task, task_title=task_title)
        team = get_object_or_404(Team, id=task.team.id)
        return task, team
    
class DeleteTaskView(LoginRequiredMixin, View):
    def get(self, request, task_title):
        task = get_object_or_404(Task, task_title=task_title)
        id = task.team.id
        task.delete()
        return redirect('team_dashboard', id=id)

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

        form = EmailVerificationForm()
        return render(self.request, 'email_verify.html', {'form': form})
    
    def post(self, request):
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "We have sent you an email please check your inbox!")
        else:
            messages.add_message(request, messages.ERROR, "User not found please check your details again")

        return render(self.request, 'email_verify.html', {'form': form})
    

class ChangePassword(FormView):
    template_name = 'new_password.html'
    form_class = NewPasswordMixin

    def validate_token(self, token):
        try:
            user = User.objects.filter(email_verification_token=uuid.UUID(str(token))).first()
            return user
        except:
            return None

    def get(self, *args, **kwargs):
        token = kwargs.get('token')
        user = self.validate_token(token)

        if user:
            return render(self.request,'new_password.html', {'token': token, 'form' : NewPasswordMixin()})
        else:
            messages.add_message(self.request, messages.ERROR, "User not found")
            return redirect(self.get_fail_redirect_url())

    def post(self, request, **kwargs):
        token = kwargs.get('token')
        user = self.validate_token(token)

        form = NewPasswordMixin(request.POST)

        if form.is_valid():
            
            user.email_verification_token = None
            form.save(user)
            return redirect(self.get_success_redirect_url())
        else:
            messages.add_message(self.request, messages.ERROR, "Password Invalid!")
            return render(self.request,'new_password.html', {'token': token, 'form' : form})

    def form_valid(self, form):
        form.save(self.user)
        return super().form_valid(form)

    def get_success_redirect_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('log_in')
    
    def get_fail_redirect_url(self):
        messages.add_message(self.request, messages.ERROR, "User not found!")
        return reverse('email_verify')

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

# ALL TEAM RELATED VIEWS

class CreateTeamView(LoginRequiredMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = CreateTeamForm
    template_name = "create_team.html"

    
    def form_valid(self, form):
        team = form.save()
        team.save()

        team.members.add(self.request.user)
        messages.add_message(self.request, messages.SUCCESS, "Team created successfully!")
        return redirect('team_dashboard', id=team.id)

class TeamDashboardView(LoginRequiredMixin, View):
    """Display the dashboard for a specific team."""
    def parse_date(self, date):
        """Parse a date string in YYYY-MM-DD format."""
        return datetime.strptime(date, '%Y-%m-%d').date()

    def get(self, request, id):
        # Retrieve the team by id, or show a 404 error if not found
        team = get_object_or_404(Team, id=id)
        tasks = Task.objects.filter(team=team)
        # You can add more context data as needed
        context = (
            {
            'team_name': team.team_name,
            'team_description': team.team_description,
            'members': team.members.all(),
            'created_at': team.created_at,
            'id': id,
            'tasks' : tasks
            # Add more context data here
            }
        )

        addFile = filter_function(request)
        context.update(addFile)
        if request.user in team.members.all():
            return render(request, 'team_dashboard.html', context)
        else:
            return redirect('dashboard')
    
class CreateTaskView(LoginRequiredMixin, View):
    """Display the dashboard for a specific team."""

    def get(self, request, id):
        team = get_object_or_404(Team, id=id)
        form = CreateTaskForm(team_id=id)
        context = {
            'form': form,
            'team_name': team.team_name,
            'team_description': team.team_description,
            'members': team.members.all(),
            'created_at': team.created_at,
            'id': team.id,
        }

        return render(request, 'edit_task.html', context)

    def post(self, request, id):
        team = get_object_or_404(Team, id=id)
        tasks = Task.objects.filter(team=team)
        form = CreateTaskForm(request.POST, team_id=id)

        if form.is_valid():
            form.save()
            return redirect('team_dashboard', id=id)
        else:
            context = {
                'form': form, 
                'team_name': team.team_name,
                'team_description': team.team_description,
                'members': team.members.all(),
                'created_at': team.created_at,
                'id': team.id,
                'tasks' : tasks,
            }
            return render(request, 'edit_task.html', context)
    
class RemoveMembersView(LoginRequiredMixin, View):
    """View to display a page for removing members from a team."""

    template_name = 'remove_member.html'

    def get(self, request, id):
        team = get_object_or_404(Team, id=id)

        context = {'team': team}
        return render(request, self.template_name, context)

    def post(self, request, id):
        team = get_object_or_404(Team, id=id)

        members_to_remove_ids = request.POST.getlist('members_to_remove')

        if not members_to_remove_ids:
            messages.add_message(request, messages.WARNING, "No members selected.")
            return render(request, self.template_name, {'team': team})

        for member_id in members_to_remove_ids:
            member_to_remove = get_object_or_404(User, id=member_id)
            if member_to_remove in team.members.all():
                team.members.remove(member_to_remove)
                messages.add_message(request, messages.SUCCESS, f"Member {member_to_remove.username} removed successfully.")
            else:
                messages.add_message(request, messages.WARNING, f"Member {member_to_remove.username} is not in the team.")
        team.save()
        return redirect('team_dashboard', id=id)
    
class AddMembersView(LoginRequiredMixin, View):
    def get(self, request, team_id):
        form = InviteMemberForm(initial={'team_id': team_id})
        return render(self.request, 'add_members.html', {'form': form, 'team_id': team_id})

    def post(self, request, team_id):
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Invitation sent successfully!")
        else:
            messages.add_message(request, messages.ERROR, "This user is either already in the team or does not exist!")

        return render(self.request, 'add_members.html', {'form': form, 'team_id': team_id})
    
class LeaveTeamView(LoginRequiredMixin, View):
    def get(self, request, id):
        team = get_object_or_404(Team, id=id)
        team.members.remove(request.user)
        messages.add_message(request, messages.SUCCESS, "You've successfully left the team!")
        if team.members.count() == 0:
            team.delete()
        return redirect('dashboard')
    
class DeleteTeamView(LoginRequiredMixin, View):
    def get(self, request, id):
        team = get_object_or_404(Team, id=id)
        team.delete()
        messages.add_message(request, messages.SUCCESS, "You've successfully deleted the team!")
        return redirect('dashboard')
    
class JoinTeamView(View):
    get_fail_redirect_url = 'link_expired'
    def get(self, *args, **kwargs):
        token = kwargs.get('token')
        team_id = self.request.GET.get('team_id')  # Extract team_id from URL parameters
        user, team = self.get_user_and_team(token, team_id)
        
        if user and team_id:
            team.members.add(user)
            messages.add_message(self.request, messages.SUCCESS, "You've successfully joined the team!")
            return redirect('team_dashboard', id=team_id)
        else:
            messages.add_message(self.request, messages.ERROR, "Invalid or expired invitation")
            return redirect(self.get_fail_redirect_url)
    
    def get_user_and_team(self, token, team_id):
        try:
            user = User.objects.filter(email_verification_token=uuid.UUID(str(token))).first()
            team = Team.objects.get(id=team_id)
            return user, team
        except:
            return None, None
        
class LinkExpiredView(View):
    def get(self, request):
        return render(request, 'link_expired.html')