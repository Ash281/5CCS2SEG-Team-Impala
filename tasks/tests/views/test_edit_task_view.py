import datetime
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTaskForm
from tasks.models import Team, User, Task

class EditTaskTestCase(TestCase):
    """Tests of the edit task view."""

    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.user = User.objects.get(username ='@johndoe')
        self.task = Task.objects.get(task_title ='Task 1')
        self.url = reverse('edit_task', args=[self.task.task_title])

        self.form_input = {
            "task_title": "Task 1",
            "task_description": "Updated decription",
            "due_date": "2024-10-10",
            "jelly_points":"1",
            "assignees": [1],
            "priority": "LW",
            "status": "IN_PROGRESS"
        }

    def test_edit_task_url(self):
        newString = self.task.task_title.replace(" ", "%20")
        self.assertEqual(self.url, f'/tasks/edit/{newString}/')

    def test_get_edit_task(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'task_title': self.task.task_title})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTaskForm))
        self.assertFalse(form.is_bound)

   
    def test_unsuccesful_edit_task(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['task_description'] = 'Te'
        before_count = Task.objects.count()
        old_description = self.task.task_description

        response = self.client.post(self.url, data=self.form_input, task_title=self.task.task_title, follow=True)
        after_count = Task.objects.count()
        task = Task.objects.get(task_title="Task 1")

        self.assertEqual(after_count, before_count)
        self.assertEqual(old_description, task.task_description)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_task.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateTaskForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid)
    
    def test_succesful_edit_task(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        old_description = self.task.task_description
        response = self.client.post(self.url, data=self.form_input, task_title=self.task.task_title, follow=True)
        after_count = Task.objects.count()
        task = Task.objects.get(task_title="Task 1")

        self.assertEqual(after_count, before_count)
        self.assertNotEqual(old_description, task.task_description)

        response_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')
        task = Task.objects.get(task_title='Task 1')
        self.assertEqual(task.task_description, 'Updated decription')
        self.assertEqual(task.due_date, datetime.date(2024, 10, 10))
        self.assertEqual(task.jelly_points, 1)
        self.assertIn(User.objects.get(pk=1), self.task.assignees.all())
        self.assertEqual(task.priority, 'LW')
        self.assertEqual(task.status, 'IN_PROGRESS')
        self.assertEqual(task.team, self.team)
        self.assertEqual(task.hours_spent, "")
        

    def test_post_edit_task_redirects_when_task_editted(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Task.objects.count()
        response = self.client.post(self.url, data=self.form_input, task_title=self.task.task_title, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('team_dashboard', args=[self.team.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'team_dashboard.html')

