"""Unit tests for the Team Manager model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Team, User

class TeamManagerTestCase(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

        self.team = Team.objects.get(team_name='Team Impala')

        self.team.members.add(self.user)

    def test_create_team(self):
        team = Team.objects.create_team(team_name='Test Team', team_description='Test Description')

        self.assertIsNotNone(team.id)
        self.assertEqual(team.team_name, 'Test Team')
        self.assertEqual(team.team_description, 'Test Description')

        self.assertTrue(Team.objects.filter(team_name='Test Team').exists())

    def test_team_creation_with_empty_name(self):
        with self.assertRaises(ValueError):
            Team.objects.create_team(team_name='', team_description='Test Description')
    
    def test_team_creation_with_empty_description(self):
        with self.assertRaises(ValueError):
            Team.objects.create_team(team_name='Test Team', team_description='')

