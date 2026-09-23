from django.http import HttpResponse
from django.views import View


class QuestionListView(View):
    # TODO(Suetone): RF4, LoginRequiredMixin + ListView using Question.objects.visible_to(user)
    def get(self, request):
        return HttpResponse('TODO: question list')
