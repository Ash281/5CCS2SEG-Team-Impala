"""Unit Tests of the create team form."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTeamForm
from tasks.models import Team

class CreateTeamFormTestCase(TestCase):
    """Unit tests of the create team form."""

    # fixtures = [
    #     'tasks/tests/fixtures/default_team.json'
    # ]

    def setUp(self):
        self.form_input = {
            'team_name': 'Team Impala',
            'team_description': 'SEG Group Project',
        }

    def test_form_has_necessary_fields(self):
        form = CreateTeamForm()
        self.assertIn('team_name', form.fields)
        self.assertIn('team_description', form.fields)
       
    def test_valid_team_form(self):
        form = CreateTeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_team_name_must_not_be_empty(self):
        self.form_input['team_name'] = ''
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_team_name_must_be_longer_than_3_characters(self):
        self.form_input['team_name'] = 'Te'
        form = CreateTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
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

    def test_form_must_save_correctly(self):
        team = Team.objects.get(team_name='Team Impala')
        form = CreateTeamForm(instance=team, data=self.form_input)
        before_count = Team.objects.count()
        form.save()
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(team.team_name, 'Team Impala')
        self.assertEqual(team.team_description, 'SEG Group Project')
