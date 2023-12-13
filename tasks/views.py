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

from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, CreateTeamForm
from tasks.helpers import login_prohibited
from tasks.models import User, Team

from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, CreateTaskForm
from tasks.helpers import login_prohibited
from .models import Task
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date

from tasks.forms import LogInForm, NewPasswordMixin, PasswordForm, EmailVerificationForm, UserForm, SignUpForm, InviteMemberForm
from tasks.helpers import login_prohibited
from .models import User

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    first_three = Task.objects.order_by('due_date')[:3]
    next_three = Task.objects.order_by('due_date')[3:6]
    user_teams = current_user.teams.all()


    return render(request, 'dashboard.html', {'user': current_user, 'first_three': first_three, 'next_three': next_three, 'user_teams': user_teams})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

# def create_task(request, id):
#     team = get_object_or_404(Team, pk=id)
#     if request.method == 'POST':
#         form = CreateTaskForm(request.POST, id=team.id)
#         if form.is_valid():
#             form.save()
        
#     else:
#         form = CreateTaskForm(id=team.id)

#     return render(request, 'create_task.html', {'form': form})

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

def my_teams(request):
    current_user = request.user
    user_teams = current_user.teams.all()

    return render(request, 'my_teams.html', {'user_teams': user_teams})

def my_tasks(request):
    current_user = request.user
    user_teams = current_user.teams.all()
    tasks = Task.objects.filter(assignees=current_user.id)

    return render(request, 'my_tasks.html', {'user_teams': user_teams, 'user_tasks': tasks})

def task_detail(request, task_title):
    task = get_object_or_404(Task, pk=task_title)
    return render(request, 'task_detail.html', {'task': task})


def edit_task(request, task_title):
    task = get_object_or_404(Task, task_title=task_title)
    team = get_object_or_404(Team, id=task.team.id)
    print(team.members.all())
    if request.method == 'POST':
        form = CreateTaskForm(request.POST, team_id=team.id, instance=task)
        if form.is_valid():
            form.save()
            return redirect('team_dashboard', id=task.team.id) 
    else:
        form = CreateTaskForm(team_id=team.id, instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task, 'members':team.members.all()})


@require_POST
def mark_task_complete(request, task_title):
    task = get_object_or_404(Task, task_title=task_title)
    days = int(request.POST.get('days', 0))
    hours_per_day = int(request.POST.get('hours', 0))
    total_hours_spent = days * hours_per_day
    task.status = 'COMPLETED'
    task.hours_spent = total_hours_spent
    task.save()
    return render(request, 'task_detail.html', {'task': task})

def delete_task(request, task_title):
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

# ALL TEAM RELATED VIEWS

class CreateTeamView(LoginRequiredMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = CreateTeamForm
    template_name = "create_team.html"

    
    def form_valid(self, form):
        # messages.add_message(self.request, messages.SUCCESS, "Team created successfully!")
        # print(self.object)
        # return super().form_valid(form)

        team = form.save()
        team.save()

        team.members.add(self.request.user)
        messages.add_message(self.request, messages.SUCCESS, "Team created successfully!")
        # print("Newly created team ID:", team.id)
        return redirect('team_dashboard', id=team.id)



class TeamDashboardView(LoginRequiredMixin, View):
    """Display the dashboard for a specific team."""

    def get(self, request, id):
        # Retrieve the team by id, or show a 404 error if not found
        team = get_object_or_404(Team, id=id)
        tasks = Task.objects.filter(team=team)
        priority_choices = {
            'high_priority': 'HI',
            'med_priority': 'MD',
            'low_priority': 'LW'
        }
        priority = priority_choices[request.GET.get('filter_by', 'due_date')]
        # You can add more context data as needed
        context = {
            'team_name': team.team_name,
            'team_description': team.team_description,
            'members': team.members.all(),
            'created_at': team.created_at,
            'id': id,
            'tasks' : tasks,
            'priority' : priority
            # Add more context data here
        }

        # return reverse('team_dashboard')
        if request.user in team.members.all():
            return render(request, 'team_dashboard.html', context)
        else:
            return redirect('dashboard')
    
# class CreateTaskView(LoginRequiredMixin, View):
#     """Display the dashboard for a specific team."""

#     def get(self, request, id):
#         # Retrieve the team by id, or show a 404 error if not found
#         team = get_object_or_404(Team, id=id)

#         # You can add more context data as needed
#         context = {
#             'team_name': team.team_name,
#             'team_description': team.team_description,
#             'members': team.members.all(),
#             'created_at': team.created_at,
#             'id': id
#             # Add more context data here
#         }
#         if request.method == 'POST':
#             form = CreateTaskForm(request.POST, id=id)
#             if form.is_valid():
#                 form.save()
            
#         else:
#             form = CreateTaskForm(id=id)

#         return render(request, 'create_task.html', context)
    
class CreateTaskView(LoginRequiredMixin, View):
    """Display the dashboard for a specific team."""

    def get(self, request, id):
        # Retrieve the team by id, or show a 404 error if not found
        team = get_object_or_404(Team, id=id)

        # Initialize the form with team_id
        form = CreateTaskForm(team_id=id)  # Change here

        # Prepare the context data
        context = {
            'form': form,  # Include the form in the context
            'team_name': team.team_name,
            'team_description': team.team_description,
            'members': team.members.all(),
            'created_at': team.created_at,
            'id': id
        }

        return render(request, 'edit_task.html', context)

    def post(self, request, id):
        # Retrieve the team by id, or show a 404 error if not found
        team = get_object_or_404(Team, id=id)

        # Initialize the form with POST data and team_id
        form = CreateTaskForm(request.POST, team_id=id)  # Change here

        if form.is_valid():
            # Save the form and do any other necessary logic
            form.save()
            return redirect('team_dashboard', id=id)
        # If the form is not valid, render the page with the form errors
        else:
            context = {
                'form': form,  # Include the form in the context
                'team_name': team.team_name,
                'team_description': team.team_description,
                'members': team.members.all(),
                'created_at': team.created_at,
                'id': id
            }
            return render(request, 'edit_task.html', context)
    
class RemoveMembersView(LoginRequiredMixin, View):
    """View to display a page for removing members from a team."""

    template_name = 'remove_member.html'  # Create a new template for this view

    def get(self, request, id):
        team = get_object_or_404(Team, id=id)

        # Ensure that the logged-in user is the owner of the team
        # if request.user != team.owner:
        #     messages.add_message(request, messages.WARNING, "You do not have permission to remove members.")
        #     return redirect('team_dashboard', id=team.id)

        context = {'team': team}
        return render(request, self.template_name, context)

    def post(self, request, id):
        team = get_object_or_404(Team, id=id)

        # Ensure that the logged-in user is the owner of the team
        # if request.user != team.owner:
        #     messages.add_message(request, messages.WARNING, "You do not have permission to remove members.")
        #     return redirect('team_dashboard', id=team.id)

        members_to_remove_ids = request.POST.getlist('members_to_remove')

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
            print(team_id)
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
    def get(self, *args, **kwargs):
        token = kwargs.get('token')
        team_id = self.request.GET.get('team_id')  # Extract team_id from URL parameters
        user = self.validate_token(token)

        if user and team_id:
            # Add the user to the team
            team = Team.objects.get(id=team_id)
            team.members.add(user)

            messages.add_message(self.request, messages.SUCCESS, "You've successfully joined the team!")
            return redirect('team_dashboard', id=team_id)
        else:
            messages.add_message(self.request, messages.ERROR, "Invalid or expired invitation")
            return redirect(self.get_fail_redirect_url())
    
    def validate_token(self, token):
        try:
            user = User.objects.filter(email_verification_token=uuid.UUID(str(token))).first()
            return user
        except:
            return None