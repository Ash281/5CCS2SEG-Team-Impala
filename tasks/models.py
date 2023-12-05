from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from libgravatar import Gravatar

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import IntegrityError

import datetime
from .validators import validate_not_past_date

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    email_verification_token = models.UUIDField(null=True, blank=True)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

class TeamManager(models.Manager):
    def create_team(self, team_name, team_description):
        """Create a new team."""

        team = self.create(team_name=team_name, team_description=team_description)
        return team
    
class Team(models.Model):
    """Models for representing a team."""

    objects = TeamManager()

    team_name = models.CharField(max_length=50, blank=False, validators=[MinLengthValidator(3, message="Team name must be a minimum of 3 characters")])
    team_description = models.CharField(max_length=150, blank=False, validators=[MinLengthValidator(10, message="Team description must be a minimum of 10 characters")])

    members = models.ManyToManyField(User, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model options."""

        ordering = ['team_name', 'team_description']

    def __str__(self):
        """String representation of the team."""
        return self.team_name
    
    def description(self):
        """String representation of the team's description."""
        return self.team_description
    
    def duration(self):
        """Return the duration since the team was created."""

        now = timezone.now()
        duration = now - self.created_at

        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f'{days} days, {hours} hours'
        elif hours > 0:
            return f'{hours} hours, {minutes} minutes'
        else:
            return f'{minutes} minutes, {seconds} seconds'

class Task(models.Model):
    PRIORITY_CHOICES = [ ('HI', 'High'), ('MD', 'Medium'), ('LW', 'Low'), ]

    task_title = models.CharField(max_length = 50, default='', blank=False, unique=True, validators=[MinLengthValidator(3, message="Title must be a minimum of 3 characters")])
    task_description = models.CharField(max_length = 500, default='', blank=False,  validators=[MinLengthValidator(10, message="Description must be a minimum of 10 characters")])
    due_date = models.DateField(default=datetime.date.today, validators=[validate_not_past_date])
    # assignees = models.CharField(max_length = 50, default='')
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='LW')
    # assignees = models.ModelMultipleChoiceField(
    #     queryset=TeamMember.objects.all(),
    #     required=False
    # )
    assignees = models.ManyToManyField(User, blank=True, related_name='assigned_tasks')
    hours_spent = models.CharField(max_length = 500, default='', blank=False)

    STATUS_CHOICES = [('NOT_STARTED', 'Not Completed'), ('COMPLETED', 'Completed') ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='NOT_STARTED')
    def __str__(self):
        return self.task_title

