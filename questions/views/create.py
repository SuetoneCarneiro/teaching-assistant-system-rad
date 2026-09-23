from django.http import HttpResponse
from django.views import View


class QuestionCreateView(View):
    # TODO(Pedro): RF3, LoginRequiredMixin + CreateView with QuestionForm, author = request.user
    def get(self, request):
        return HttpResponse('TODO: open a question')
