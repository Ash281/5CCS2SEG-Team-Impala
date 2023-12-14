"""Tests of the create team view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTeamForm
from tasks.models import Team, User

class RemoveMembersViewTestCase(TestCase):
    """Tests of the create team view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.form_input = {
            'team_name': 'Test Team',
            'team_description': 'This team purposed is testing',
            'created_at':'2019-03-01 00:00:00',
            'members':[]
        }
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('remove_members', args=[self.team.id])

    def test_remove_members_url(self):
        self.assertEqual(self.url,f'/remove_members/{self.team.id}/')

    def test_get_remove_members(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'remove_member.html')

    def test_successful_remove_member(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.team.members.count()
        response = self.client.post(self.url, data={'members_to_remove':[self.user.id]}, follow=True)
        after_count = self.team.members.count()
        self.assertEqual(after_count, before_count-1)
        #self.assertRedirects(response, self.url, status_code=302, target_status_code=200)
        #self.assertTemplateUsed(response, 'remove_member.html')

    def test_unsuccessful_remove_member(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.team.members.count()
        response = self.client.post(self.url, data={'members_to_remove':[0]}, follow=True)
        after_count = self.team.members.count()
        self.assertEqual(after_count, before_count)
        #self.assertRedirects(response, url=reverse('team', args=[self.team.id]), status_code=302, target_status_code=200)
        #self.assertTemplateUsed(response, 'remove_member.html')