"""Unit tests for the Task model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Task, Team, User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
import datetime

class TaskTestCase(TestCase):
    """Unit tests for the Task model."""

    fixtures = [

        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/default_task.json',
        'tasks/tests/fixtures/other_tasks.json'
    ]

    def setUp(self):
        self.task = Task.objects.get(task_title='Task 1')
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username="@janedoe")
        self.team = Team.objects.get(team_name="Team Impala")

    def test_valid_task(self):
        self._assert_task_is_valid()
    
    def test_str_method(self):
        task = Task(task_title="Test Task", task_description="Test Description")
        self.assertEqual(str(task), "Test Task")

    def test_title_cannot_be_blank(self): 
        self.task.task_title = ''
        self._assert_task_is_invalid()

    def test_description_cannot_be_blank(self): 
        self.task.task_description = ''
        self._assert_task_is_invalid()

    def test_title_can_be_50_characters_long(self): 
        self.task.task_title = 'x' * 50
        self._assert_task_is_valid()

    def test_description_can_be_500_characters_long(self):  
        self.task.task_description = 'x' * 500
        self._assert_task_is_valid()

    def test_title_cannot_be_over_50_characters_long(self): 
        self.task.task_title = 'x' * 51
        self._assert_task_is_invalid()

    def test_description_cannot_be_over_500_characters_long(self):
        self.task.task_description = 'x' * 501
        self._assert_task_is_invalid()

    def test_title_must_be_unique(self):  
        second_task = Task.objects.get(task_title='Task 2')
        self.task.task_title = second_task.task_title
        self._assert_task_is_invalid()

    def test_description_need_not_be_unique(self):  
        second_task = Task.objects.get(task_title='Task 2')
        self.task.task_description = second_task.task_description
        self._assert_task_is_valid()

    def test_title_must_contain_at_least_3_characters(self): 
        self.task.task_title = '1!'
        self._assert_task_is_invalid()

    def test_description_must_contain_at_least_10_characters(self):  
        self.task.task_description = 'task desc'
        self._assert_task_is_invalid()

    def test_title_may_contain_numbers(self): 
        self.task.task_title = 'task 2'
        self._assert_task_is_valid()
    
    ### Test task assignees field ###

    def test_assignees_can_be_blank(self): 
        self.task.assignees.clear()
        self.task.save()
        self._assert_task_is_valid()

    def test_assignees_must_be_in_team(self):
        for assignee in self.task.assignees.all():
            self.assertIn(assignee, self.team.members.all())
    
    ### Test task due date field ###

    def test_due_date_cannot_be_before_today(self): 
        self.task.due_date = timezone.now().date() - timedelta(days=1)
        self._assert_task_is_invalid()

    def test_due_date_can_be_after_today(self): 
        self.task.due_date = timezone.now().date() + timedelta(days=1)
        self._assert_task_is_valid()

    ### Test task status field ###

    def test_task_status_can_be_not_completed(self):
        valid_status_choices = [status[0] for status in Task.STATUS_CHOICES]
        my_status = 'TODO'
        self.assertIn(my_status, valid_status_choices)
        self.task.status = my_status
        self.task.save()
        self.assertEqual(self.task.status, my_status)
        self._assert_task_is_valid()

    def test_task_status_can_be_in_progress(self):
        valid_status_choices = [status[0] for status in Task.STATUS_CHOICES]
        my_status = 'IN_PROGRESS'
        self.assertIn(my_status, valid_status_choices)
        self.task.status = my_status
        self.task.save()
        self.assertEqual(self.task.status, my_status)
        self._assert_task_is_valid()

    def test_task_status_can_be_completed(self):
        valid_status_choices = [status[0] for status in Task.STATUS_CHOICES]
        my_status = 'DONE'
        self.assertIn(my_status, valid_status_choices)
        self.task.status = my_status
        self.task.save()
        self.assertEqual(self.task.status, my_status)
        self._assert_task_is_valid()
    
    def test_task_status_cannot_be_anything_else(self):
        valid_status_choices = [status[0] for status in Task.STATUS_CHOICES]
        my_status = 'NOT_VALID'
        self.assertNotIn(my_status, valid_status_choices)
        self.task.status = my_status
        self._assert_task_is_invalid()

    ### Test task priority field ###
   
    def test_task_priority_can_be_low(self):
        valid_priority_choices = [status[0] for status in Task.PRIORITY_CHOICES]
        my_priority = 'LW'
        self.assertIn(my_priority, valid_priority_choices)
        self.task.priority = my_priority
        self.task.save()
        self.assertEqual(self.task.priority, my_priority)
        self._assert_task_is_valid()

    def test_task_priority_can_be_med(self):
        valid_priority_choices = [status[0] for status in Task.PRIORITY_CHOICES]
        my_priority = 'MD'
        self.assertIn(my_priority, valid_priority_choices)
        self.task.priority = my_priority
        self.task.save()
        self.assertEqual(self.task.priority, my_priority)

        self._assert_task_is_valid()

    def test_task_priority_can_be_high(self):
        valid_priority_choices = [status[0] for status in Task.PRIORITY_CHOICES]
        my_priority = 'HI'
        self.assertIn(my_priority, valid_priority_choices)
        self.task.priority = my_priority
        self.task.save()
        self.assertEqual(self.task.priority, my_priority)
        self._assert_task_is_valid()

    def test_task_priority_cannot_be_anything_else(self):
        valid_priority_choices = [status[0] for status in Task.PRIORITY_CHOICES]
        my_priority = 'INVALID'
        self.assertNotIn(my_priority, valid_priority_choices)
        self.task.priority = my_priority
        self._assert_task_is_invalid()
    
    ### Test jelly points field ###
    def test_jelly_points_default_is_one(self):
        self.assertEqual(self.task.jelly_points, 1)

    def test_task_jelly_points_cannot_be_negative(self): 
        self.task.jelly_points = -1
        self._assert_task_is_invalid()

    def test_task_jelly_points_cannot_be_zero(self): 
        self.task.jelly_points = 0
        self._assert_task_is_invalid()

    def test_jelly_points_can_be_positive_with_range(self):
        self.task.jelly_points = 5
        self._assert_task_is_valid()
    
    def test_jelly_points_can_be_50(self):
        self.task.jelly_points = 50
        self._assert_task_is_valid()

    def test_task_jelly_points_cannot_be_over_50(self):
        self.task.jelly_points = 51
        self._assert_task_is_invalid()
    
    ### Test task created_at field ###

    def test_task_created_at_cannot_be_null(self):
        self.assertIsNotNone(self.task.created_at)
    
    def test_created_at_less_than_equal(self):
        self.assertLessEqual(self.task.created_at, timezone.now())
    
    ### Test task hours_spent field ###

    def test_hours_spent_can_be_blank(self):
        self.task.hours_spent = ''
        self._assert_task_is_valid()

    def test_hours_spent_accepts_valid_data(self):
        self.task.hours_spent = '5'
        self._assert_task_is_valid()
    
    def test_hours_spent_cannot_be_over_500_characters(self):
        self.task.hours_spent = 'x' * 501  
        self._assert_task_is_invalid()

    ### Test duration for tasks ###

    def test_duration_with_days(self):
        task = Task.objects.create(task_title="Test Task", task_description="Test Description")
        fixed_now = timezone.now()
        task.created_at = fixed_now - datetime.timedelta(days=2, hours=3, minutes=30)  

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(task.duration(), '2 days, 3 hours')

    def test_duration_with_hours_and_minutes(self):
        task = Task.objects.create(task_title="Test Task", task_description="Test Description")
        fixed_now = timezone.now()
        task.created_at = fixed_now - datetime.timedelta(hours=5, minutes=45)

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(task.duration(), '5 hours, 45 minutes')

    def test_duration_with_minutes_and_seconds(self):
        task = Task.objects.create(task_title="Test Task", task_description="Test Description")
        fixed_now = timezone.now()
        task.created_at = fixed_now - datetime.timedelta(minutes=12, seconds=30)

        with patch('django.utils.timezone.now', return_value=fixed_now):
            self.assertEqual(task.duration(), '12 minutes, 30 seconds')

    

    def _assert_task_is_valid(self):
        try:
            self.task.full_clean()
        except (ValidationError):
            self.fail('Task should be valid')

    def _assert_task_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.task.full_clean()