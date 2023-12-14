"""Tests of the create team view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTeamForm
from tasks.models import Team, User

class CreateTeamTestCase(TestCase):
    """Tests of the create team view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.form_input = {
            'team_name': 'Test Team',
            'team_description': 'This team purposed is testing',
            'created_at':'2019-03-01 00:00:00',
            'members':[]
        }
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('create_team')

    def test_create_team_url(self):
        self.assertEqual(self.url,'/create_team/')

    def test_get_create_team(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTeamForm))
        self.assertFalse(form.is_bound)

       
    def test_unsuccesful_create_team(self):
        self.client.login(username=self.user.username, password='Password123')
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
        self.assertFalse(form.is_valid())

    
    def test_succesful_create_team(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        team = Team.objects.get(team_name="Test Team")
        response_url = reverse('team_dashboard', args=[team.id])
        self.assertEqual(team.team_description, 'This team purposed is testing')
        self.assertEqual(team.members.count(), 1)
        
    def test_post_create_team_redirects_when_team_created(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.post(self.url, data=self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        team = Team.objects.get(team_name="Test Team")
        redirect_url = reverse('team_dashboard', args=[team.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
