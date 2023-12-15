"""Unit Tests for the Team model."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTeamForm
from tasks.models import Team
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.utils import timezone
import datetime

class TeamModelTestCase(TestCase):
    """Unit tests for the Team model."""

    fixtures = [
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json'
    ]

    def setUp(self):
        self.form_input = {
            'team_name': 'Team Impala',
            'team_description': 'SEG Group Coursework Project',
            'created_at' : '2020-03-01 00:00:00',
        }
    
    def test_str_method(self):
        team = Team(team_name="Test Team", team_description="Test Description")
        self.assertEqual(str(team), "Test Team")

    def test_description_method(self):
        team = Team(team_name="Test Team", team_description="Test Description")
        self.assertEqual(team.description(), "Test Description")
    
    def test_duration_with_days(self):
        team = Team.objects.create(team_name="Test Team", team_description="Test Description")
        fixed_now = timezone.now()
        team.created_at = fixed_now - datetime.timedelta(days=2, hours=5, minutes=30)

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(team.duration(), '2 days, 5 hours')

    def test_duration_with_hours_and_minutes(self):
        team = Team.objects.create(team_name="Test Team", team_description="Test Description")
        fixed_now = timezone.now()
        team.created_at = fixed_now - datetime.timedelta(hours=3, minutes=45)

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(team.duration(), '3 hours, 45 minutes')

    def test_duration_with_minutes_and_seconds(self):
        team = Team.objects.create(team_name="Test Team", team_description="Test Description")
        fixed_now = timezone.now()
        team.created_at = fixed_now - datetime.timedelta(minutes=12, seconds=30)

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(team.duration(), '12 minutes, 30 seconds')
    
    ### Test team name ###

    def test_team_name_must_not_be_empty(self):
        self.form_input['team_name'] = ''
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_team_name_must_be_longer_than_3_characters(self):
        self.form_input['team_name'] = 'Te'
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('team_name', form.errors)
    
    def test_team_name_must_be_shorter_than_50_characters(self):
        self.form_input['team_name'] = 'T' * 51
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_team_name_is_exactly_3_characters(self):
        self.form_input['team_name'] = 'Tea'
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_team_name_is_exactly_50_characters(self):
        self.form_input['team_name'] = 'T' * 50
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    ### Test team description ###

    def test_team_description_must_not_be_empty(self):
        self.form_input['team_description'] = ''
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('team_description', form.errors)

    def test_team_description_must_be_longer_than_10_characters(self):
        self.form_input['team_description'] = '!descr'
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_team_description_must_be_shorter_than_150_characters(self):
        self.form_input['team_description'] = 'd' * 151
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_team_description_is_exactly_10_characters(self):
        self.form_input['team_description'] = 'd' * 10
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_team_description_is_exactly_150_characters(self):
        self.form_input['team_description'] = 'd' * 150
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    ### Test team created_at field ###
    def test_valid_created_at(self):
        self.form_input['created_at'] = '2020-03-01 00:00:00'
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_team_created_at_must_not_be_empty(self):
        team = Team.objects.create(team_name="Example Team", team_description="Example Description")
        self.assertIsNotNone(team.created_at)
    
    def test_team_created_at_must_be_in_the_past(self):
        self.form_input['created_at'] = '2021-03-01 00:00:00'
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def _assert_team_is_valid(self):
        try:
            self.team.full_clean()
        except (ValidationError):
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.team.full_clean()
