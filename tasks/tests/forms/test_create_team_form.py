"""Unit tests of the sign up form."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTeamForm
from tasks.models import Team

class CreateTeamFormTestCase(TestCase):
    """Unit tests of the create team form."""

    def setUp(self):
        self.form_input = {
            'team_name': 'Team Impala',
            'team_description': 'SEG Group Coursework Project',
            'created_at' : '2020-03-01 00:00:00',
        }

    def test_valid_create_team_form(self):
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateTeamForm()
        self.assertIn('team_name', form.fields)
        self.assertIn('team_description', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['team_name'] = 'Te'
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateTeamForm(data=self.form_input)
        before_count = Team.objects.count()
        form.save()
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        team = Team.objects.get(team_name='Team Impala')
        self.assertEqual(team.team_name, 'Team Impala')
        self.assertEqual(team.team_description, 'SEG Group Coursework Project')
