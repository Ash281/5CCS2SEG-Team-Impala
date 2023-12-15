"""Tests of the Email Verification view."""
import uuid
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team

class DeleteTeamViewTestCase(TestCase):
    """Tests of the join team view."""

    fixtures = ['tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.user = User.objects.get(username='@janedoe')
        self.team = Team.objects.get(team_name='Team Impala')
        self.url = reverse('delete_team', args=[self.team.id])
    
    def test_delete_team_url(self):
        self.assertEqual(self.url,f'/team/{self.team.id}/delete/')
        
    def test_get_delete_team(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Team.objects.count()
        response = self.client.get(self.url, {'task_title': self.team.team_name}, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(before_count, after_count+1)
        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        #self.assertTemplateUsed(response, 'team_dashboard.html')
