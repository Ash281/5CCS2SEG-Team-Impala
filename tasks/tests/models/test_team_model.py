"""Unit Tests for the Team model."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTeamForm
from tasks.models import Team
from django.core.exceptions import ValidationError


class TeamModelTestCase(TestCase):
    """Unit tests for the Team model."""

    def setUp(self):
        self.form_input = {
            'team_name': 'Team Impala',
            'team_description': 'SEG Group Coursework Project',
            'created_at' : '2020-03-01 00:00:00',
        }
    
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
    
    def _assert_team_is_valid(self):
        try:
            self.team.full_clean()
        except (ValidationError):
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.team.full_clean()
