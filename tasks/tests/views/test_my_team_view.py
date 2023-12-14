import datetime
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from tasks.forms import CreateTaskForm
from tasks.models import Team, User, Task

class MyTeamsViewTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json',
                'tasks/tests/fixtures/default_task.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('my_teams')

    def test_authenticated_user_can_access_view(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_teams.html')

    def test_user_teams_and_user_tasks(self):
        self.client.login(username=self.user.username, password='Password123')

        # Assuming the fixtures provide the necessary data for teams and tasks
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_teams.html')

        # Check if user_teams and user_tasks are in the context
        self.assertIn('user_teams', response.context)
        self.assertIn('user_tasks', response.context)
    
    
