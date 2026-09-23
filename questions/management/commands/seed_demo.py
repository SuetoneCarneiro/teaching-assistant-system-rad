"""Create the demo data described in PLAN.md section 11.

Safe to run more than once: existing rows are reused, never duplicated.
Passwords always go through create_user / create_superuser (hashed).
"""

from datetime import time

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from accounts.roles import PROFESSORS_GROUP, STUDENTS_GROUP
from questions.models import Question, Subject
from schedules.models import OfficeHour

PASSWORD = 'Monitoria@2026'

Status = Question.Status

QUESTIONS = [
    # (subject, author, assigned monitor, status, title, description, answer)
    (
        'RAD101', 'student_ana', None, Status.OPEN,
        'How do I use related_name?',
        'My Question model has two foreign keys to User and makemigrations '
        'fails with a "reverse accessor clashes" error. What is going on?',
        '',
    ),
    (
        'RAD101', 'student_bruno', 'monitor_carla', Status.IN_PROGRESS,
        'Why does my migration fail?',
        'After renaming a field, migrate says the column does not exist. '
        'Should I delete the migrations folder?',
        '',
    ),
    (
        'RAD101', 'student_ana', 'monitor_carla', Status.ANSWERED,
        'LoginRequiredMixin vs @login_required',
        'When should I use the mixin and when should I use the decorator?',
        'They do the same job. Use @login_required on function-based views '
        'and LoginRequiredMixin on class-based views. The mixin must come '
        'first (leftmost) in the class bases.',
    ),
    (
        'RAD101', 'student_bruno', 'monitor_carla', Status.CLOSED,
        'What is a QuerySet?',
        'The slides say filter() returns a QuerySet. Is that a list?',
        'A QuerySet is a lazy description of a database query. It only hits '
        'the database when you iterate, slice or evaluate it, and you can '
        'keep chaining filter() calls before that happens.',
    ),
    (
        'WEB201', 'student_ana', None, Status.OPEN,
        'Flexbox vs Grid?',
        'Which one should I use to lay out a card list?',
        '',
    ),
    (
        'WEB201', 'student_bruno', 'monitor_extra', Status.ANSWERED,
        'What does CSRF protect?',
        'Why does Django ask for {% csrf_token %} in every POST form?',
        'CSRF (cross-site request forgery) is when another site makes your '
        'browser send a request to ours using your session. The token proves '
        'the form was rendered by our site, so forged POSTs are rejected.',
    ),
]


class Command(BaseCommand):
    help = 'Create groups, test accounts, subjects and questions for the demo.'

    def handle(self, *args, **options):
        students, _ = Group.objects.get_or_create(name=STUDENTS_GROUP)
        professors, _ = Group.objects.get_or_create(name=PROFESSORS_GROUP)
        professors.permissions.add(
            Permission.objects.get(
                codename='view_all_questions',
                content_type__app_label='questions',
            )
        )

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', PASSWORD)

        users = {
            'student_ana': self.user('student_ana', 'Ana', 'Souza', students),
            'student_bruno': self.user('student_bruno', 'Bruno', 'Lima', students),
            'monitor_carla': self.user('monitor_carla', 'Carla', 'Mendes', students),
            'professor_diego': self.user('professor_diego', 'Diego', 'Ramos', professors),
            'monitor_extra': self.user('monitor_extra', 'Eva', 'Costa', students),
        }

        subjects = {}
        for code, name, is_active, monitors in [
            ('RAD101', 'Rapid Application Development', True, ['monitor_carla']),
            ('WEB201', 'Web Programming', True, ['monitor_extra']),
            ('DB301', 'Databases', False, []),
        ]:
            subject, _ = Subject.objects.update_or_create(
                code=code, defaults={'name': name, 'is_active': is_active}
            )
            subject.monitors.set([users[username] for username in monitors])
            subjects[code] = subject

        for code, author, monitor, status, title, description, answer in QUESTIONS:
            Question.objects.get_or_create(
                title=title,
                defaults={
                    'subject': subjects[code],
                    'author': users[author],
                    'assigned_monitor': users[monitor] if monitor else None,
                    'status': status,
                    'description': description,
                    'answer': answer,
                },
            )

        # Optional challenge (schedules app): two office hours for Carla in RAD101.
        for weekday, start, end in [
            (OfficeHour.Weekday.MONDAY, time(9), time(10)),
            (OfficeHour.Weekday.WEDNESDAY, time(14), time(16)),
        ]:
            OfficeHour.objects.get_or_create(
                monitor=users['monitor_carla'],
                subject=subjects['RAD101'],
                weekday=weekday,
                start_time=start,
                end_time=end,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready. Every account uses the password {PASSWORD!r}.'
        ))

    def user(self, username, first_name, last_name, group):
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(
                username,
                password=PASSWORD,
                first_name=first_name,
                last_name=last_name,
            )
        user.groups.add(group)
        return user
