from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

from schedules.models import OfficeHour

from ..forms import QuestionForm
from ..models import Question


class QuestionCreateView(LoginRequiredMixin, CreateView):
    """RF3: any authenticated user can open a question in an active subject."""

    model = Question
    form_class = QuestionForm
    template_name = 'questions/question_form.html'

    def get_initial(self):
        initial = super().get_initial()
        subject = self.request.GET.get('subject')
        if subject:
            initial['subject'] = subject
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Office hours of every active subject, grouped by subject. The page
        # shows the group of the selected subject (?subject= or the POSTed one).
        slots = (
            OfficeHour.objects.filter(subject__is_active=True)
            .select_related('subject', 'monitor')
            .order_by('subject__code', 'weekday', 'start_time')
        )
        groups = {}
        for slot in slots:
            groups.setdefault(slot.subject, []).append(slot)
        context['office_hours'] = list(groups.items())
        selected = str(context['form']['subject'].value() or '')
        context['selected_subject'] = selected
        context['selected_has_slots'] = any(str(subject.pk) == selected for subject in groups)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Your question was opened. A monitor will pick it up soon.')
        return response

    def get_success_url(self):
        return reverse('questions:detail', args=[self.object.pk])
