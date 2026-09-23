from django.http import HttpResponse
from django.views import View


class QuestionDetailView(View):
    # TODO(Suetone): RF9, LoginRequiredMixin + DetailView with can_claim / can_answer / can_close
    def get(self, request, pk):
        return HttpResponse(f'TODO: question {pk}')


class AnswerView(View):
    # TODO(Suetone): RF6, LoginRequiredMixin + UserPassesTestMixin + UpdateView (POST only)
    def post(self, request, pk):
        return HttpResponse(f'TODO: answer question {pk}')
