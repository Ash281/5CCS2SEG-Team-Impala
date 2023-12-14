import datetime
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTaskForm
from tasks.models import Team, User, Task


class DashboardTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('dashboard')
        

    def test_authenticated_user_dashboard(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(response.context['user'], self.user)
    
    def test_to_do_task_counts(self):
        self.client.login(username=self.user.username, password='Password123')
        self.task.status = 'TODO'
        self.task.save()
        response = self.client.get(self.url)
        
        self.assertEqual(response.context['to_do_tasks'], 1)

    def test_in_progress_task_counts(self):
        self.client.login(username=self.user.username, password='Password123')
        self.task.status = 'IN_PROGRESS'
        # self.task.assignees.set([1])
        self.task.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['in_progress'], 1)


    def test_done_task_counts(self):
        self.client.login(username=self.user.username, password='Password123')
        self.task.status = 'DONE'
        self.task.save()
        response = self.client.get(self.url)
        
        self.assertEqual(response.context['done'], 1)


    
