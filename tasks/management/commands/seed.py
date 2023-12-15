import datetime
import random
from django.core.management.base import BaseCommand, CommandError

from tasks.models import User, Team, Task

import pytz
from faker import Faker
from random import randint

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'email_verification_token' : '', 'jelly_points': '0'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'email_verification_token' : '', 'jelly_points': '0'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'email_verification_token' : '', 'jelly_points': '0'},
]

team_fixtures = [
    { "team_name": "Team Impala", "team_description" : "SEG Group Coursework Project", "members" :[1], "created_at" : "2023-01-01T12:00:00Z", "team_admins": ""},
    { "team_name": "Team 1", "team_description" : "SEG Group Coursework Project", "members" :[1], "created_at" : "2023-01-01T12:00:00Z", "team_admins": ""},
    { "team_name": "Team 2", "team_description" : "SEG Group Coursework Project", "members" :[1], "created_at" : "2023-01-01T12:00:00Z", "team_admins": ""},
]

task_fixtures = [
    {"task_title": "Task 1",
      "task_description": "Using this for our website :)",
      "due_date": "2024-10-10",
      "created_at":"2023-01-01T12:00:00Z",
      "hours_spent":"",
      "jelly_points":"1",
      "assignees": [1],
      "priority": "LW",
      "team":1,
      "status": "TODO" },

    {"task_title": "Task 2",
      "task_description": "Using this for our website :)",
      "due_date": "2024-10-10",
      "created_at":"2023-01-01T12:00:00Z",
      "hours_spent":"",
      "jelly_points":"1",
      "assignees": [1],
      "priority": "LW",
      "team":1,
      "status": "TODO" },

    {"task_title": "Task 3",
      "task_description": "Using this for our website :)",
      "due_date": "2024-10-10",
      "created_at":"2023-01-01T12:00:00Z",
      "hours_spent":"",
      "jelly_points":"1",
      "assignees": [1],
      "priority": "LW",
      "team":1,
      "status": "TODO" },

     ]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 30
    TEAM_COUNT = 10
    TASK_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()

        self.create_teams()
        self.teams = Team.objects.all()

        self.create_tasks()
        self.tasks = Task.objects.all()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def create_teams(self):
        self.generate_team_fixtures()
        self.generate_random_teams()

    def create_tasks(self):
        self.generate_task_fixtures()
        self.generate_random_tasks()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_team_fixtures(self):
        for data in team_fixtures:
            self.try_create_team(self)
   
    def generate_task_fixtures(self):
        for data in task_fixtures:
            self.try_create_task(self)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_random_teams(self):
        team_count = Team.objects.count()
        while  team_count < self.TEAM_COUNT:
            print(f"Seeding team {team_count}/{self.TEAM_COUNT}", end='\r')
            self.generate_team()
            last_team = Team.objects.all()[team_count]
            self.add_members_to_team(last_team)
            team_count = Team.objects.count()

        print("Teams seeding complete.      ")

    def add_members_to_team(self, team):
        number_of_users_to_pick = random.randint(0, User.objects.count())
        users_list = list(User.objects.all())
        randomly_picked_users = random.sample(users_list, number_of_users_to_pick)
        team.members.set(randomly_picked_users)
 
    def get_random_user_from_team(self, team):
        team_users = Team.objects.get(id=team.id).members
        
        number_of_users_to_pick = random.randint(0, team_users.count())
        users_list = list(team_users.all())
        randomly_picked_users = random.sample(users_list, number_of_users_to_pick)
        return randomly_picked_users

    def generate_random_tasks(self):
        task_count = Task.objects.count()
        while  task_count < self.TASK_COUNT:
            print(f"Seeding task {task_count}/{self.TASK_COUNT}", end='\r')
            self.generate_task()

            task_count = Task.objects.count()
        print("Tasks seeding complete.      ")

    def add_members_to_task(self, task):
        get_team = task.team
        team_members = Team.objects.get(id=get_team.id)
        number_of_users_to_pick = random.randint(0, team_members.count())
        randomly_picked_users = random.sample(team_members, number_of_users_to_pick)
        task.assignees.set(randomly_picked_users)

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def generate_team(self):
        team_name = self.create_string(3, 50)
        team_description = self.create_string(10, 150)
        self.try_create_team({'team_name': team_name, 'team_description': team_description})
       
    def generate_task(self):
        PRIORITY_CHOICES = [('HI', 'High'), ('MD', 'Medium'), ('LW', 'Low')]
        STATUS_CHOICES = [ ('TODO', 'Not Completed'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Completed'), ]

        task_name = self.create_string(3, 50)
        task_description = self.create_string(10, 500)
        due_date= self.faker.date(pattern='%Y-%m-%d'),
        jelly_points= self.faker.random_int(min=1, max=50),
        priority= self.faker.random_element(elements=PRIORITY_CHOICES),
        team = get_random_team(),
        assignees = self.get_random_user_from_team(team[0]),
        status= self.faker.random_element(elements=STATUS_CHOICES),
        self.try_create_task({
            "task_title": task_name,
            "task_description": task_description,
            "due_date": due_date,
            "jelly_points":jelly_points,
            "assignees": assignees,
            "priority": priority,
            "status": status,
            "team" : team
            })
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass
    
    def try_create_team(self, data):
        try:
            self.create_team(data)
        except:
            pass
    
    def try_create_task(self, data):
        try:
            self.create_task(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_team(self, data):
        Team.objects.create(
            team_name=data['team_name'],
            team_description=data['team_description'],
        )        

    def create_task(self, data):
        assignees = data.get('assignees')[0]
        team = data.get('team')[0]
        
        try:
            team_obj = Team.objects.get(id=team.id)
        except Team.DoesNotExist:
            print("Team doesnt exist")
            # Handle the case when the team doesn't exist
            return None
                
        task1 = Task.objects.create(
            task_title=data['task_title'],
            task_description=data['task_description'],
            due_date=datetime.date.today() + datetime.timedelta(days=7),
            hours_spent='',
            jelly_points=data['jelly_points'][0],
            priority=data['priority'],
            team=team,
            status=data['status'][0]
        )
        task1.assignees.set(assignees)
       

    def create_string(self, min, max):
        random_string = self.faker.text(max_nb_chars=max)
        return random_string


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def get_random_user():
    user_ids = list(User.objects.values_list('id', flat=True))  # Convert QuerySet to a list
    random_id = random.choice(user_ids)
    user = User.objects.get(id=random_id)
    return user

def get_random_team():
    index = randint(0, Team.objects.count() -1 )
    return Team.objects.all()[index]
