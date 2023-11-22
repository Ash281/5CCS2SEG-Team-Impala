"""Unit tests of the create tasks form."""
from django import forms
from django.test import TestCase
from tasks.forms import CreateTaskForm
from tasks.models import Task
import datetime

class CreateTaskFormFormTestCase(TestCase):
    """Unit tests of the create tasks form."""

    fixtures = [
        'tasks/tests/fixtures/default_task.json'
    ]

    def setUp(self):
        self.form_input = {
            'task_title': 'Task 2',
            'task_description': 'Using this for our website 2 :)',
            'due_date': '2023-11-23',
            'assignees': 'xxxxx',
        }

    def test_form_has_necessary_fields(self):
        form = CreateTaskForm()
        self.assertIn('task_title', form.fields)
        self.assertIn('task_description', form.fields)
        self.assertIn('due_date', form.fields)
        self.assertIn('assignees', form.fields)
       
    def test_valid_task_form(self):
        form = CreateTaskForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['task_title'] = 'Ta'
        form = CreateTaskForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        task = Task.objects.get(task_title='Task 1')
        form = CreateTaskForm(instance=task, data=self.form_input)
        before_count = Task.objects.count()
        form.save()
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(task.task_title, 'Task 2')
        self.assertEqual(task.task_description, 'Using this for our website 2 :)')
        self.assertEqual(task.due_date, datetime.date(2023, 11, 23))
        self.assertEqual(task.assignees, 'xxxxx')
