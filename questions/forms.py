from django import forms

from .models import Question


class QuestionForm(forms.Form):
    # TODO(Pedro): RF3, ModelForm with fields = ['subject', 'title', 'description'],
    # subject queryset limited to active subjects.
    pass


# ---------------------------------------------------------------------------


class AnswerForm(forms.ModelForm):
    """RF6: only the answer text. Status changes happen in the view."""

    class Meta:
        model = Question
        fields = ['answer']
        widgets = {
            'answer': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Explain the solution step by step...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # blank=True on the model (it starts empty), but required here.
        # The form field strips whitespace, so "   " is also rejected.
        self.fields['answer'].required = True
