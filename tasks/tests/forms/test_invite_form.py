"""Unit tests of the sign up form."""
from django.core.mail import send_mail
from django.core import mail
from django import forms
from django.test import TestCase
from tasks.forms import InviteMemberForm
from tasks.models import Team, User
import uuid

class InviteMemberFormTestCase(TestCase):
    """Unit tests of the create team form."""
    fixtures = ['tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/default_team.json']
    
    def setUp(self):
        self.team = Team.objects.get(team_name='Team Impala')
        self.token = str(uuid.uuid4())
        self.user = User.objects.get(username='@johndoe')
        self.user.email_verification_token = self.token
        self.user.save()
        self.form_input = {
            'team_id': 1,
            'username': '@janedoe'
        }

    def test_valid_invite_form(self):
        form = InviteMemberForm(data=self.form_input)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = InviteMemberForm()
        self.assertIn('team_id', form.fields)
        self.assertIn('username', form.fields)

    def test_invite_member_form_user_already_in_team(self):
        team = Team.objects.get(id=self.team.id)
        team.members.add(self.user)
        data = {'team_id': self.team.id, 'username': '@johndoe'}
        form = InviteMemberForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'User is already in the team!')

    def test_invite_member_form_user_not_found(self):
        data = {'team_id': self.team.id, 'username': 'nonexistentuser'}
        form = InviteMemberForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], 'User not found!')

    def test_email_sent_to_user(self):
        data = {'team_id': self.team.id, 'username': '@janedoe'}
        form = InviteMemberForm(data)
        self.assertTrue(form.is_valid())
        form.save()
        user_to_add = User.objects.get(username='@janedoe')
        self.assertEqual(len(mail.outbox), 1)

        # Check the content of the email
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [User.objects.get(username='@janedoe').email])
        self.assertEqual(sent_email.subject, 'Invite Link')
        self.assertEqual(sent_email.body, f"Hi there, \nThis is your link to join Team: http://127.0.0.1:8000/join_team/{user_to_add.email_verification_token}?team_id={self.team.id}")

    def test_invite_member_form_save(self):
        form_data = {'team_id': 1, 'username': 'testuser'}
        form = InviteMemberForm(data=form_data)
        form.save()
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verification_token)