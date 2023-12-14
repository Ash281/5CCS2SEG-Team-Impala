from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.forms import FilterPriorityForm,FilterDateRangeForm,SearchTaskForm
from datetime import date

class MyTaskViewTestCase(TestCase):
    """Tests of the delete task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('my_tasks')

    def test_my_tasks_url(self):
        self.assertEqual(self.url, '/my_tasks/')

    def test_get_my_tasks(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        user = response.context.get('user')
        team = response.context.get('user_teams')
        task = response.context.get('user_tasks')
        self.assertEqual(user.username, self.user.username)
        self.assertIn(self.task, task)
        self.assertIn(self.team, team)
        self.assertTemplateUsed(response, 'my_tasks.html')

