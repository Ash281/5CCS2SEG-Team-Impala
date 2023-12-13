"""Unit tests of the create tasks form."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTaskForm
from tasks.models import Task, Team
import datetime

class CreateTaskFormFormTestCase(TestCase):
    """Unit tests of the create tasks form."""

    fixtures = [
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_task.json'
    ]

    def setUp(self):
        self.team = Team.objects.get(team_name="Team Impala")
        self.form_input = {
            "task_title": "Test Task",
            "task_description": "Using this for our website :)",
            "due_date": "2024-10-10",
            "jelly_points":"1",
            "assignees": [1],
            "priority": "LW",
            "status": "TODO"
        }


    def test_form_has_necessary_fields(self):
        form = CreateTaskForm(team_id=self.team.id)
        self.assertIn('task_title', form.fields)
        self.assertIn('task_description', form.fields)
        self.assertIn('due_date', form.fields)
        self.assertIn('assignees', form.fields)
        self.assertIn('jelly_points', form.fields)
        self.assertIn('priority', form.fields)
        self.assertIn('status', form.fields)
       
    def test_valid_task_form(self):
        form = CreateTaskForm(data=self.form_input, team_id=self.team.id)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['task_title'] = 'Ta'
        form = CreateTaskForm(data=self.form_input, team_id=self.team.id)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        task = Task.objects.get(task_title='Task 1')
        form = CreateTaskForm(instance=task, data=self.form_input, team_id=self.team.id)
        before_count = Task.objects.count()
        form.save()
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(task.task_title, 'Test Task')
        self.assertEqual(task.task_description, 'Using this for our website 2 :)')
        self.assertEqual(task.due_date, datetime.date(2023, 11, 23))
   