from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from ..models import Question

# Both views check WHO first (403) and only then the HTTP method (405), so
# typing the URL in the browser also answers "Access denied".
# They change the system state, so they only accept POST: GET must be safe
# (links can be prefetched or followed by crawlers) and POST is covered by
# Django's CSRF protection.


@login_required
def claim_question(request, pk):
    """RF5: a monitor of the subject claims an Open question."""
    question = get_object_or_404(Question.objects.select_related('subject'), pk=pk)

    if not question.is_monitor(request.user):
        raise PermissionDenied
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if question.author_id == request.user.pk:
        messages.error(request, 'You cannot claim a question you asked yourself.')
        return redirect(question)

    # Conditional UPDATE: the database only changes the row if it is still
    # open and unassigned. If two monitors click at the same time, the second
    # one updates 0 rows.
    claimed = Question.objects.filter(
        pk=question.pk,
        status=Question.Status.OPEN,
        assigned_monitor__isnull=True,
    ).update(
        assigned_monitor=request.user,
        status=Question.Status.IN_PROGRESS,
        updated_at=timezone.now(),
    )

    if claimed:
        messages.success(request, 'You claimed this question. Write the answer below.')
    else:
        messages.error(request, 'This question is no longer open. Another monitor may have claimed it.')
    return redirect(question)


@login_required
def close_question(request, pk):
    """RF7: the author confirms the answer solved the question."""
    question = get_object_or_404(Question, pk=pk)

    if question.author_id != request.user.pk:
        raise PermissionDenied
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if not question.can_be_closed_by(request.user):
        if question.status == Question.Status.CLOSED:
            messages.error(request, 'This question is already closed.')
        else:
            messages.error(request, 'Only answered questions can be closed.')
        return redirect(question)

    question.status = Question.Status.CLOSED
    question.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Question marked as resolved. It is now part of the knowledge base.')
    return redirect(question)
