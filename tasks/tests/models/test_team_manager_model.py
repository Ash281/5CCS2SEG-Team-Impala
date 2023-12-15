"""Unit tests for the Team Manager model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Team, User

class TeamManagerTestCase(TestCase):
    def setUp(self):
        # self.team = Team.objects.get(team_name='Team Impala')
        # self.user = User.objects.get(username='@johndoe')
        # self.second_user = User.objects.get(username="@janedoe")
        # self.task = Task.objects.get(task_title='Task 1')
        # self.second_task = Task.objects.get(task_title='Task 2')

        # Create a user if your Team model requires it
        user = User.objects.create(username='@testuser', password='Testpassword123')

        # Create a team object for testing
        self.team = Team.objects.create(
            team_name='Team Impala',
            team_description='SEG Group Coursework Project'
        )

        # Add the user to the team if necessary
        self.team.members.add(user)

    def test_create_team(self):
        team = Team.objects.create_team(team_name='Test Team', team_description='Test Description')

        self.assertIsNotNone(team.id)
        self.assertEqual(team.team_name, 'Test Team')
        self.assertEqual(team.team_description, 'Test Description')

        self.assertTrue(Team.objects.filter(team_name='Test Team').exists())

    def test_team_creation_with_invalid_data(self):
        with self.assertRaises(ValueError):
            Team.objects.create_team(team_name='', team_description='Test Description')

