from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from ..models import Question


@login_required
def knowledge_base(request):
    """RF8: answered and closed questions from everyone, searchable by ?q=."""
    query = request.GET.get('q', '').strip()
    questions = Question.objects.knowledge_base().select_related('subject')
    if query:
        questions = questions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'questions/knowledge_base.html', {
        'questions': questions,
        'query': query,
    })
