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
    
    ### Test team members field ###
    # def test_team_members_must_not_be_empty(self):
    #     empty_member_data = {
    #         'team_name': 'Test Team', 
    #         'team_description': 'Test Description', 
    #         'members': []
    #     }
    #     form = CreateTeamForm(data=empty_member_data)
    #     self.assertFalse(form.is_valid())
    
    # def test_team_members_must_be_valid(self):
    #     invalid_member_data = {
    #         'team_name': 'Test Team', 
    #         'team_description': 'Test Description', 
    #         'members': [9999]  
    #     }
    #     form = CreateTeamForm(data=invalid_member_data)
    #     self.assertFalse(form.is_valid())
    
    def _assert_team_is_valid(self):
        try:
            self.team.full_clean()
        except (ValidationError):
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    # def test_remove_member(self):
    #     # Test removing an existing member
    #     member_to_remove = Team.objects.get(name="Test User 1")
    #     member_count_before = Team.objects.count()

    #     # Call your remove member function
    #     member_to_remove.remove_member()

    #     # Check if the member was removed
    #     self.assertEqual(Team.objects.count(), member_count_before - 1)
    #     self.assertFalse(Team.objects.filter(name="Test User 1").exists())