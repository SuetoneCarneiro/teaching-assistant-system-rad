from django.http import HttpResponse


def claim_question(request, pk):
    # TODO(Suetone): RF5, @login_required, monitor of the subject only, POST only, OPEN -> IN_PROGRESS
    return HttpResponse(f'TODO: claim question {pk}')


def close_question(request, pk):
    # TODO(Suetone): RF7, @login_required, author only, POST only, ANSWERED -> CLOSED
    return HttpResponse(f'TODO: close question {pk}')
