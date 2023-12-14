import datetime
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task

class DeleteTaskTestCase(TestCase):
    """Tests of the delete task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.second_user = User.objects.get(username ='@janedoe')
        self.url = reverse('leave_team', args=[self.team.id])

    def test_delete_task_url(self):
        self.assertEqual(self.url, f'/leave_team/{self.team.id}/')

    def test_get_leave_team_with_one_member(self):
        self.client.login(username=self.user.username, password='Password123')
        before_team_count = Team.objects.count()
        before_member_count = self.team.members.count()
        self.assertEqual(before_member_count, 1)

        response = self.client.get(self.url, follow=True)
        after_team_count = Team.objects.count()
        self.assertEqual(before_team_count, after_team_count+1)

        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
    
    def test_get_leave_team_with_more_members(self):
        self.client.login(username=self.user.username, password='Password123')
        self.team.members.add(self.second_user)

        before_team_count = Team.objects.count()
        before_member_count = self.team.members.count()
        self.assertGreater(before_member_count, 1)

        response = self.client.get(self.url, follow=True)
        after_team_count = Team.objects.count()
        after_member_count = self.team.members.count()
        self.assertEqual(before_team_count, after_team_count)
        self.assertEqual(before_member_count, after_member_count+1)

        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_get_leave_team_with_invalid_team_id(self):
        self.client.login(username=self.user.username, password='Password123')
        invalid_team_id = 5
        self.url = reverse('leave_team', args=[invalid_team_id])

        before_team_count = Team.objects.count()
        before_member_count = self.team.members.count()

        response = self.client.get(self.url, follow=True)
        after_team_count = Team.objects.count()
        after_member_count = self.team.members.count()
        self.assertEqual(before_team_count, after_team_count)
        self.assertEqual(before_member_count, after_member_count)
  
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')