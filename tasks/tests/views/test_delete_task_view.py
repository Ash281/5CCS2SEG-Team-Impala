import datetime
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task

class DeleteTaskTestCase(TestCase):
    """Tests of the delete task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('delete_task', args=[self.task.task_title])

    def test_delete_task_url(self):
        newString = self.task.task_title.replace(" ", "%20")
        self.assertEqual(self.url, f'/tasks/delete/{newString}/')

    def test_get_delete_task(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.get(self.url, {'task_title': self.task.task_title}, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(before_count, after_count+1)
        response_url = reverse('team_dashboard', args=[self.team.id])  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
