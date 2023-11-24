"""Tests of the create team view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTeamForm
from tasks.models import Team

class CreateTeamTestCase(TestCase):
    """Tests of the create team view."""

    fixtures = ['tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.url = reverse('create_team')
        self.form_input = {
            'team_name': 'Team Impala',
            'team_description': 'SEG Group Coursework Project',
            'created_at':'2019-03-01 00:00:00',
        }
        self.team = Team.objects.get(team_name='Team Impala')

    def test_create_team_url(self):
        self.assertEqual(self.url,'/create_team/')

    def test_get_create_team(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTeamForm))
        self.assertFalse(form.is_bound)

    def test_get_create_team_redirects_when_team_created(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('team_dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')

    def test_unsuccesful_create_team(self):
        self.form_input['team_name'] = 'Te'
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTeamForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_create_team(self):
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('team_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
        team = Team.objects.get(team_name='Team Impala')
        self.assertEqual(team.team_name, 'Team Impala')
        self.assertEqual(team.team_description, 'SEG Group Coursework Project')

    def test_post_create_team_redirects_when_team_created(self):
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('team_dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
