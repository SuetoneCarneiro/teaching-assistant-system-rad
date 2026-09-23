from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

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

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Your question was opened. A monitor will pick it up soon.')
        return response

    def get_success_url(self):
        return reverse('questions:detail', args=[self.object.pk])
