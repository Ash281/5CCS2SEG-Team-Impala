"""Tests of the Email Verification view."""
import uuid
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team

class JoinTeamTestCase(TestCase):
    """Tests of the join team view."""

    fixtures = ['tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.user = User.objects.get(username='@janedoe')
        self.team = Team.objects.get(team_name='Team Impala')
        self.user.email_verification_token = str(uuid.uuid4())
        self.user.save()
        self.user.refresh_from_db()
        self.url = reverse('join_team', args=[self.user.email_verification_token])
        
    def test_join_team_url_with_valid_token_user_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertEqual(self.url, f'/join_team/{self.user.email_verification_token}/')
        response = self.client.get(self.url, {'team_id':self.team.id}, follow=True)
        redirect_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
    

    def test_join_team_url_with_valid_token_user_logged_out(self):
        self.assertEqual(self.url, f'/join_team/{self.user.email_verification_token}/')
        response = self.client.get(self.url, {'team_id':self.team.id}, follow=True)
        login_required = reverse('log_in')
        aim_to_url = reverse('team_dashboard', args=[self.team.id])
        redirect_url = f'{login_required}?next={aim_to_url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    
    def test_join_team_url_with_different_token(self):
        self.client.login(username=self.user.username, password='Password123')
        different_token_url = f'/join_team/{str(uuid.uuid4())}/'
        self.assertNotEqual(self.url, different_token_url)
        response = self.client.get(different_token_url, follow=True)
        redirect_url = reverse('link_expired')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'link_expired.html')

    
    def test_succesful_join_team(self):        
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.team.members.count()
        self.assertEqual(self.url, f'/join_team/{self.user.email_verification_token}/')
        response = self.client.get(self.url, {'team_id':self.team.id}, follow=True)
        after_count = self.team.members.count()
        self.assertEqual(after_count, before_count+1)
        self.assertIn(self.user, self.team.members.all())
        redirect_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')

    def test_join_team_url_with_invalid_team_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertEqual(self.url, f'/join_team/{self.user.email_verification_token}/')
        wrong_team_id = 9
        response = self.client.get(self.url, {'team_id': wrong_team_id}, follow=True)
        redirect_url = reverse('link_expired')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'link_expired.html')
    