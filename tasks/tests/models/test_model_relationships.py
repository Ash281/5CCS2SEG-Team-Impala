from django.test import TestCase
from tasks.models import Task, Team, User
from django.core.exceptions import ValidationError

class ModelRelationshipTestCase(TestCase):

    fixtures = [
            'tasks/tests/fixtures/default_user.json',
            'tasks/tests/fixtures/other_users.json',
            'tasks/tests/fixtures/default_team.json',
            'tasks/tests/fixtures/default_task.json',
        ]

    def setUp(self):

        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username="@janedoe")

        self.task = Task.objects.get(task_title='Task 1')
        self.team = Team.objects.get(team_name="Team Impala")

    def test_adding_assignees_to_task(self):
        self.task.assignees.add(self.user, self.second_user)
        self.assertIn(self.user, self.task.assignees.all())
        self.assertIn(self.second_user, self.task.assignees.all())

    def test_removing_assignees_from_task(self):
        self.task.assignees.add(self.user, self.second_user)
        self.task.assignees.remove(self.user)
        self.assertNotIn(self.user, self.task.assignees.all())
        self.assertIn(self.second_user, self.task.assignees.all())

    def test_association_of_task_with_team(self):
        self.assertEqual(self.task.team, self.team)

    def test_change_task_team(self):
        new_team = Team.objects.create(team_name='New Team', team_description='Another team')
        self.task.team = new_team
        self.task.save()
        self.assertEqual(self.task.team, new_team)
    
    def test_assign_task_to_user_not_in_team_raises_error(self):
        self.task = Task.objects.create(task_title='Test Task', task_description='Test Description')
        self.user_without_team = User.objects.create(username='user_no_team', email='user_no_team@example.com')

        with self.assertRaises(ValidationError):
            self.task.assignees.add(self.user_without_team)
            self.task.full_clean()  
