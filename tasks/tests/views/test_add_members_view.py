"""Tests of the Email Verification view."""
import uuid
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import InviteMemberForm
from tasks.models import User, Team

class AddMembersViewTestCase(TestCase):
    """Tests of the join team view."""

    fixtures = ['tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.user = User.objects.get(username='@janedoe')
        self.team = Team.objects.get(team_name='Team Impala')
        self.url = reverse('add_members', args=[self.team.id])
        self.form_input = {
            'team_id': self.team.id,
            'username': '@janedoe'
        }
    
    def test_add_members_url(self):
        self.assertEqual(self.url,f'/team/{self.team.id}/add_members/')
        
    def test_valid_add_members_form(self):
        self.client.login(username=self.user.username, password='Password123')
        form = InviteMemberForm(data=self.form_input)
        response = self.client.post(self.url, {'username': '@janedoe', 'team_id': self.team.id, 'form': form})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')
        self.assertTrue(response.context['form'].is_valid())
        self.assertContains(response, 'Invitation sent successfully!')
    
    def test_add_members_form_user_already_in_team(self):
        self.client.login(username=self.user.username, password='Password123')
        team = Team.objects.get(id=self.team.id)
        team.members.add(self.user)
        response = self.client.post(self.url, {'username': '@janedoe', 'team_id': self.team.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')
        self.assertFormError(response, 'form', 'username', 'User is already in the team!')
