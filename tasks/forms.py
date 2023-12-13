"""Forms for the tasks app."""
import uuid
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator

from .models import User, Team

from task_manager import settings

from django.core.mail import send_mail
from .models import User
from .models import Task


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class EmailVerificationForm(forms.Form):
    username = forms.CharField(max_length=100)

    def clean(self):
        super().clean()
        try:
            self.username = self.cleaned_data.get("username")
            user = User.objects.get(username=self.username)
        except:
            self.add_error('username', 'User not found!')
        return self.cleaned_data
    
    def save(self):
        if self.is_valid():
            username = self.cleaned_data.get("username")
            user = User.objects.get(username=username)

            token = str(uuid.uuid4())
            self.send_email_verification(user.email, token)

            user.email_verification_token = token
            user.save()        
    
    
    def send_email_verification(self, email, token):
        subject = 'Reset Password Link'
        body = f"Hi there, \nThis is your link to reset your password: http://127.0.0.1:8000/new_password/{token}/"
        send_mail(subject, body, settings.EMAIL_HOST_USER, [email])

class InviteMemberForm(forms.Form):
    team_id = forms.IntegerField(widget=forms.HiddenInput())
    username = forms.CharField(max_length=100)

    def clean(self):
        super().clean()

        username = self.cleaned_data.get("username")
        team_id = self.cleaned_data.get("team_id")

        try:
            user = User.objects.get(username=username)
            team = Team.objects.get(id=team_id)

            # Check if the user is already in the team
            if user in team.members.all():
                self.add_error('username', 'User is already in the team!')
        except User.DoesNotExist:
            self.add_error('username', 'User not found!')

        return self.cleaned_data
    
    def save(self):
        if self.is_valid():
            username = self.cleaned_data.get("username")
            user = User.objects.get(username=username)

            token = str(uuid.uuid4())
            team_id = self.cleaned_data.get("team_id")
            self.invite_members(user.email, token, team_id)

            user.email_verification_token = token
            user.save()        

    def invite_members(self, email, token, team_id):
        subject = 'Invite Link'
        body = f"Hi there, \nThis is your link to join Team: http://127.0.0.1:8000/join_team/{token}?team_id={team_id}"
        send_mail(subject, body, settings.EMAIL_HOST_USER, [email])

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self, user):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if user is not None:
            user.set_password(new_password)
            user.save()
        return user

class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super(forms.ModelForm, self).save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )

        return user

class TeamForm(forms.ModelForm):
    """Form to update team profiles."""

    class Meta:
        """Form options."""

        model = Team
        fields = ['team_name', 'team_description']

class CreateTeamForm(forms.ModelForm):
    """Form enabling users to create teams."""
     
    class Meta:
        """Form options."""

        model = Team
        fields = ['team_name', 'team_description']

    def save(self, user=None, commit=True):
        """Create a new team."""

        team = super().save(commit=False)
        if commit:
            team.save()
            self.save_m2m()  
        return team
    
class FilterTaskForm(forms.Form):
    """Form enabling users to filter tasks."""

    PRIORITY_CHOICES = [
        ('', '--Select Priority--'),
        ('high_priority', 'High Priority'),
        ('med_priority', 'Medium Priority'),
        ('low_priority', 'Low Priority'),
    ]

    FILTER_CHOICES = [
        ('', '--Select Filter--'),
        ('date_range', 'Date Range'),
    ]

    filter_by_priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'onchange': 'showDateRange(this.value)'}),
    )

    filter_by = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'onchange': 'showDateRange(this.value)'}),
    )

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

class SearchTaskForm(forms.Form):
    """Form enabling users to search tasks."""

    search = forms.CharField(max_length=100, required=False, label='', widget=forms.TextInput(attrs={'placeholder': 'Search for a task'}))

class CreateTaskForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.team_id = kwargs.pop('team_id')
        super(CreateTaskForm, self).__init__(*args, **kwargs)

        print(f"My team my {self.team_id}")
        if self.team_id:
            self.fields['assignees'].queryset = User.objects.filter(teams__id=self.team_id)
        else:
            self.fields['assignees'].queryset = User.objects.none()

    def save(self, commit=True):
        task = super(CreateTaskForm, self).save(commit=False)
        task.team_id = self.team_id 
        if commit:
            task.save()

           
            existing_assignees = task.assignees.all()
            print(f"My assignees {existing_assignees}")
            #selected_users = [user for user in self.cleaned_data['assignees'] if user not in existing_assignees]
            task.assignees.set(self.cleaned_data['assignees'])  # Set the assignees to the selected users
            

            if self.cleaned_data['status'] == "DONE":
                task.hours_spent = task.duration()
                for user in task.assignees.all():
                    print("My jelly points")
                    user.jelly_points += task.jelly_points
                    user.save()

            task.save()

        return task

    class Meta:
        model = Task
        fields = ['task_title', 'task_description', 'due_date', 'jelly_points', 'assignees', 'priority', 'status']
        labels = {
            'task_title': 'Task title',
            'task_description': 'Task description',
            'due_date': 'Due date', 
            'priority': 'Priority',
            'status': 'Status',
            'jelly_points': 'Jelly points'
        }
        widgets = { 'task_description': forms.Textarea(), 'due_date': forms.DateInput(attrs={'type': 'date'})}
    