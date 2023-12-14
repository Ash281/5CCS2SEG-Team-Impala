from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task

class MyTaskViewTestCase(TestCase):
    """Tests of the delete task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('task_detail', args=[self.task.id])

    def test_my_tasks_url(self):
        self.assertEqual(self.url, f'/tasks/{self.task.id}/')

    def test_get_my_tasks(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        task = response.context.get('task')
        self.assertEqual(self.task, task)
        self.assertTemplateUsed(response, 'task_detail.html')
