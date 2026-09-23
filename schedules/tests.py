from datetime import time
from io import StringIO

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from questions.models import Subject

from .models import OfficeHour

PASSWORD = 'Monitoria@2026'


class OfficeHourTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', stdout=StringIO())
        cls.carla = User.objects.get(username='monitor_carla')
        cls.rad = Subject.objects.get(code='RAD101')
        cls.web = Subject.objects.get(code='WEB201')

    def slot(self, weekday, start, end, subject=None):
        return OfficeHour(
            monitor=self.carla,
            subject=subject or self.rad,
            weekday=weekday,
            start_time=start,
            end_time=end,
        )

    def test_seed_creates_two_slots_for_carla(self):
        self.assertEqual(OfficeHour.objects.filter(monitor=self.carla, subject=self.rad).count(), 2)

    def test_overlapping_slot_on_same_day_is_rejected(self):
        # Seed has Monday 09:00-10:00.
        with self.assertRaises(ValidationError):
            self.slot(OfficeHour.Weekday.MONDAY, time(9, 30), time(10, 30)).full_clean()

    def test_adjacent_slot_is_allowed(self):
        self.slot(OfficeHour.Weekday.MONDAY, time(10), time(11)).full_clean()

    def test_same_time_on_another_day_is_allowed(self):
        self.slot(OfficeHour.Weekday.TUESDAY, time(9), time(10)).full_clean()

    def test_end_must_be_after_start(self):
        with self.assertRaises(ValidationError):
            self.slot(OfficeHour.Weekday.FRIDAY, time(11), time(10)).full_clean()

    def test_only_own_subjects(self):
        with self.assertRaises(ValidationError):
            self.slot(OfficeHour.Weekday.FRIDAY, time(9), time(10), subject=self.web).full_clean()

    def test_non_monitor_gets_403(self):
        self.client.login(username='student_ana', password=PASSWORD)
        self.assertEqual(self.client.get(reverse('schedules:mine')).status_code, 403)

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse('schedules:mine'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('schedules:mine')}")

    def test_monitor_adds_slot_through_the_page(self):
        self.client.login(username='monitor_carla', password=PASSWORD)
        url = reverse('schedules:mine')
        response = self.client.post(url, {
            'subject': self.rad.pk, 'weekday': 4, 'start_time': '08:00', 'end_time': '09:00',
        })
        self.assertRedirects(response, url)
        self.assertTrue(OfficeHour.objects.filter(monitor=self.carla, weekday=4).exists())

    def test_page_shows_overlap_error_and_does_not_save(self):
        self.client.login(username='monitor_carla', password=PASSWORD)
        response = self.client.post(reverse('schedules:mine'), {
            'subject': self.rad.pk, 'weekday': 0, 'start_time': '09:30', 'end_time': '10:30',
        })
        self.assertContains(response, 'overlaps another one')
        self.assertEqual(OfficeHour.objects.filter(monitor=self.carla).count(), 2)

    def test_page_rejects_forged_subject(self):
        self.client.login(username='monitor_carla', password=PASSWORD)
        response = self.client.post(reverse('schedules:mine'), {
            'subject': self.web.pk, 'weekday': 4, 'start_time': '08:00', 'end_time': '09:00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(OfficeHour.objects.filter(subject=self.web).exists())

    def test_slots_show_on_create_page_for_the_subject(self):
        self.client.login(username='student_ana', password=PASSWORD)
        response = self.client.get(reverse('questions:create') + f'?subject={self.rad.pk}')
        self.assertContains(response, '14:00–16:00')
        self.assertNotContains(response, f'data-office-hours="{self.rad.pk}" hidden')

    def test_office_hours_link_only_for_monitors(self):
        self.client.login(username='monitor_carla', password=PASSWORD)
        self.assertContains(self.client.get(reverse('questions:list')), reverse('schedules:mine'))
        self.client.login(username='student_ana', password=PASSWORD)
        self.assertNotContains(self.client.get(reverse('questions:list')), reverse('schedules:mine'))
