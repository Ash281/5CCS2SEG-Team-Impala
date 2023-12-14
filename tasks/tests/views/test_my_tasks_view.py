from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.forms import FilterPriorityForm,FilterDateRangeForm,SearchTaskForm

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

    # def test_filter_not_none(self):
    #     # Write a test for the priority filter form
    #     self.client.login(username=self.user.username, password='Password123')
    #     form = FilterPriorityForm(['high_priority'])
    #     response = self.client.get(self.url)
    #     # priority_filter = response.context.GET.get('filter_by_priority')
    #     self.assertIsNotNone(response.context['priority'])


    # def test_filter_date_range_form(self):
    #     # Write a test for the date range filter form
    #     self.client.login(username=self.user.username, password='Password123')
    #     response = self.client.get(self.url)

    #     start_date_filter = response.context.GET.get('start_date')
    #     self.assertIsNotNone(start_date_filter)

    #     end_date_filter = response.context.GET.get('end_date')
    #     self.assertIsNotNone(end_date_filter)

    # def test_search_task_form(self):
    #     # Write a test for the search task form
    #     self.client.login(username=self.user.username, password='Password123')
    #     response = self.client.get(self.url)
    #     priority_filter = response.context.GET.get('search')
    #     self.assertIsNotNone(priority_filter)