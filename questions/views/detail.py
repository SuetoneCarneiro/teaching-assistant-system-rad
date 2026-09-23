from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, UpdateView

from ..forms import AnswerForm
from ..models import Question

STEPS = [
    Question.Status.OPEN,
    Question.Status.IN_PROGRESS,
    Question.Status.ANSWERED,
    Question.Status.CLOSED,
]


class QuestionDetailView(LoginRequiredMixin, DetailView):
    """RF9: the page only offers the actions this user can take right now."""

    model = Question
    template_name = 'questions/question_detail.html'
    context_object_name = 'question'

    def get_queryset(self):
        # Anyone else gets a 404, as if the question did not exist.
        return (
            Question.objects.readable_by(self.request.user)
            .select_related('subject', 'author', 'assigned_monitor')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        user = self.request.user

        context['can_claim'] = question.can_be_claimed_by(user)
        context['can_answer'] = question.can_be_answered_by(user)
        context['can_close'] = question.can_be_closed_by(user)
        if context['can_answer']:
            context['answer_form'] = AnswerForm(instance=question)

        current = STEPS.index(question.status)
        context['steps'] = [
            {
                'label': status.label,
                'state': 'is-done' if i < current else 'is-current' if i == current else '',
            }
            for i, status in enumerate(STEPS)
        ]
        return context


class AnswerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """RF6: only the assigned monitor answers. The status becomes Answered."""

    model = Question
    form_class = AnswerForm
    http_method_names = ['post']

    def test_func(self):
        # Runs before the HTTP method check: the author and other monitors get
        # 403 even when they just type the URL in the browser.
        return self.get_object().assigned_monitor_id == self.request.user.pk

    def form_valid(self, form):
        question = self.object
        if not question.can_be_answered_by(self.request.user):
            messages.error(self.request, 'This question no longer accepts answers.')
            return redirect(question)

        form.instance.status = Question.Status.ANSWERED
        form.save()
        messages.success(self.request, 'Answer saved. The author can now mark it as resolved.')
        return redirect(question)

    def form_invalid(self, form):
        messages.error(self.request, 'The answer cannot be blank.')
        return redirect(self.object)
