from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from ..models import Question


class QuestionListView(LoginRequiredMixin, ListView):
    """RF4: one page, three different result sets depending on who opens it."""

    model = Question
    template_name = 'questions/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return (
            Question.objects.visible_to(self.request.user)
            .select_related('subject', 'author', 'assigned_monitor')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        monitored_subjects = user.monitored_subjects.all()

        if user.has_perm('questions.view_all_questions'):
            context['heading'] = 'All questions'
            context['subheading'] = 'Every question from every subject.'
        elif monitored_subjects:
            codes = ', '.join(subject.code for subject in monitored_subjects)
            context['heading'] = 'Questions in your subjects'
            context['subheading'] = f'You monitor {codes}. Your own questions show up here too.'
        else:
            context['heading'] = 'My questions'
            context['subheading'] = 'Only you and the monitors of each subject can see these.'
        return context
