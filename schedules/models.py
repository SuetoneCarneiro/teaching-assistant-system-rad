from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from questions.models import Subject


class OfficeHour(models.Model):
    """A weekly slot when a monitor is available for one of their subjects."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='office_hours',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='office_hours',
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return (
            f'{self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}'
            f' · {self.subject.code}'
        )

    def clean(self):
        # Fields that failed their own validation are missing here: skip the
        # rules that need them, the form already shows those errors.
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'The end time must be after the start time.'})

        if self.monitor_id and self.subject_id:
            if not self.subject.monitors.filter(pk=self.monitor_id).exists():
                raise ValidationError({'subject': 'You can only add office hours for subjects you monitor.'})

        if self.monitor_id and self.weekday is not None and self.start_time and self.end_time:
            # Two slots overlap when each one starts before the other ends.
            # Touching slots (09:00-10:00 and 10:00-11:00) are allowed.
            overlapping = OfficeHour.objects.filter(
                monitor_id=self.monitor_id,
                weekday=self.weekday,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError(
                    'This slot overlaps another one of your office hours on the same day.'
                )
