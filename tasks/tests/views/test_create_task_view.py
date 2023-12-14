import datetime
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTaskForm
from tasks.models import Team, User, Task

class CreateTaskTestCase(TestCase):
    """Tests of the create task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('create_task', args=[self.team.id])

        self.form_input = {
            "task_title": "Test Task",
            "task_description": "Using this for our website :)",
            "due_date": "2024-10-10",
            "jelly_points":"1",
            "assignees": [1],
            "priority": "LW",
            "status": "IN_PROGRESS"
        }

    def test_create_create_task_url(self):
        self.assertEqual(self.url, f'/create_task/{self.team.id}/')

    def test_get_create_task(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'id': self.team.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTaskForm))
        self.assertFalse(form.is_bound)

   
    def test_unsuccesful_create_team(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['task_description'] = 'Te'
        before_count = Team.objects.count()
        response = self.client.post(self.url, data=self.form_input, id=self.team.id, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTaskForm))
        self.assertTrue(form.is_bound)
    
    def test_succesful_create_task(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, data=self.form_input, id=self.team.id, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
        task = Task.objects.get(task_title='Test Task')
        self.assertEqual(task.task_description, 'Using this for our website :)')
        self.assertEqual(task.due_date, datetime.date(2024, 10, 10))
        self.assertEqual(task.jelly_points, 1)
        self.assertIn(User.objects.get(pk=1), self.task.assignees.all())
        self.assertEqual(task.priority, 'LW')
        self.assertEqual(task.status, 'IN_PROGRESS')
        self.assertEqual(task.team, self.team)
        self.assertEqual(task.hours_spent, "")


    def test_post_create_team_redirects_when_team_created(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, data=self.form_input, id=self.team.id, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count+1)
        redirect_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')

