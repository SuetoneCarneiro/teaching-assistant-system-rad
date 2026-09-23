from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import OfficeHourForm
from .models import OfficeHour


class MyOfficeHoursView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Monitors list their office hours and add new ones on the same page."""

    model = OfficeHour
    form_class = OfficeHourForm
    template_name = 'schedules/office_hours.html'
    success_url = reverse_lazy('schedules:mine')

    def test_func(self):
        return self.request.user.monitored_subjects.exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['monitor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['office_hours'] = (
            OfficeHour.objects.filter(monitor=self.request.user).select_related('subject')
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Office hour added.')
        return super().form_valid(form)
