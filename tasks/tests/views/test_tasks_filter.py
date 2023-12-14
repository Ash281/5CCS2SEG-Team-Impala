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
        
    def test_priority_filter_url_correct(self):
        # Write a test for the priority filter form
        self.client.login(username=self.user.username, password='Password123')
        form_data = {'priority': 'high_priority'}
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        query_params = response.context['request'].GET
        self.assertIn('priority', query_params)
        self.assertEqual(query_params['priority'], 'high_priority')

    def test_date_range_filter_url_correct(self):
        # Write a test for the date range filter form
        self.client.login(username=self.user.username, password='Password123')
        form_data = {'start_date': date(2023,12,15), 'end_date': date(2030,12,31)}
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        query_params = response.context['request'].GET
        self.assertIn('start_date', query_params)
        self.assertIn('end_date', query_params)
        self.assertEqual(query_params['start_date'], '2023-12-15')
        self.assertEqual(query_params['end_date'], '2030-12-31')

    def test_search_filter_url_correct(self):
        # Write a test for the priority filter form
        self.client.login(username=self.user.username, password='Password123')
        form_data = {'search': 'hello'}
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        query_params = response.context['request'].GET
        self.assertIn('search', query_params)
        self.assertEqual(query_params['search'], 'hello')