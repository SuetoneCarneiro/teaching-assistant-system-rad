from django import forms


class QuestionForm(forms.Form):
    # TODO(Pedro): RF3, ModelForm with fields = ['subject', 'title', 'description'],
    # subject queryset limited to active subjects.
    pass


# ---------------------------------------------------------------------------


class AnswerForm(forms.Form):
    # TODO(Suetone): RF6, ModelForm with fields = ['answer'], answer required.
    pass
