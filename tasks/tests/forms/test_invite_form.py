"""Unit tests of the sign up form."""
from django import forms
from django.test import TestCase
from tasks.forms import InviteMemberForm
from tasks.models import Team, User

class InviteMemberFormTestCase(TestCase):
    """Unit tests of the create team form."""
    fixtures = ['tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']
    
    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'team_id': 1,
            'username': '@janedoe'
        }

    def test_valid_invite_form(self):
        form = InviteMemberForm(data=self.form_input)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = InviteMemberForm()
        self.assertIn('team_id', form.fields)
        self.assertIn('username', form.fields)

    def test_invite_member_form_user_already_in_team(self):
        team = Team.objects.get(id=self.team.id)
        team.members.add(self.user)
        data = {'team_id': self.team.id, 'username': '@johndoe'}
        form = InviteMemberForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'User is already in the team!')

    def test_invite_member_form_user_not_found(self):
        data = {'team_id': self.team.id, 'username': 'nonexistentuser'}
        form = InviteMemberForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'User not found!')