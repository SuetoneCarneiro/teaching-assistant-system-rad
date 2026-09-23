from django.conf import settings
from django.db import models
from django.db.models import Q


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Inactive subjects do not accept new questions.',
    )
    monitors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='monitored_subjects',
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} · {self.name}'


class QuestionQuerySet(models.QuerySet):
    def visible_to(self, user):
        """RF4: the questions the list page shows to this user, in ONE query.

        Professor -> every question.
        Student   -> only the questions they asked.
        Monitor   -> questions of the subjects they monitor (crossing
                     Question -> Subject -> monitors), plus the ones they asked.
        """
        if user.has_perm('questions.view_all_questions'):
            return self.all()
        # distinct(): the join with Subject.monitors returns one row per monitor.
        return self.filter(Q(author=user) | Q(subject__monitors=user)).distinct()

    def readable_by(self, user):
        """Detail page: what the user sees in the list, plus the knowledge base."""
        if user.has_perm('questions.view_all_questions'):
            return self.all()
        return self.filter(
            Q(author=user)
            | Q(subject__monitors=user)
            | Q(status__in=Question.PUBLIC_STATUSES)
        ).distinct()

    def knowledge_base(self):
        """RF8: answered and closed questions, no matter who asked them."""
        return self.filter(status__in=Question.PUBLIC_STATUSES)


class Question(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In progress'
        ANSWERED = 'answered', 'Answered'
        CLOSED = 'closed', 'Closed'

    PUBLIC_STATUSES = [Status.ANSWERED, Status.CLOSED]

    title = models.CharField(max_length=200)
    description = models.TextField()
    # PROTECT: a subject with questions is deactivated, never deleted.
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='questions',
    )
    # Two foreign keys point to User, so each one needs its own related_name.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions_asked',
    )
    assigned_monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions_assigned',
    )
    answer = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionQuerySet.as_manager()

    class Meta:
        ordering = ['-updated_at']
        permissions = [
            ('view_all_questions', 'Can view all questions'),
        ]

    def __str__(self):
        return self.title

    # Business rules. The views use them to protect the routes (RF5-RF7) and
    # the templates use them to show or hide the buttons (RF9). A closed
    # question fails every check, so it accepts no more changes.

    def is_monitor(self, user):
        return self.subject.monitors.filter(pk=user.pk).exists()

    def can_be_claimed_by(self, user):
        return (
            self.status == self.Status.OPEN
            and self.author_id != user.pk
            and self.is_monitor(user)
        )

    def can_be_answered_by(self, user):
        return (
            self.status in (self.Status.IN_PROGRESS, self.Status.ANSWERED)
            and self.assigned_monitor_id == user.pk
        )

    def can_be_closed_by(self, user):
        return self.status == self.Status.ANSWERED and self.author_id == user.pk
