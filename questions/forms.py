from django import forms

from .models import Question, Subject


class QuestionForm(forms.ModelForm):
    """RF3. author, assigned_monitor, answer and status are never form fields:
    the view sets the author and the model default sets the status."""

    # Limiting the queryset also rejects a forged POST with an inactive subject id.
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        empty_label='Choose a subject',
    )

    class Meta:
        model = Question
        fields = ['subject', 'title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Why does my migration fail?',
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'What did you try? What happened? Paste the error message if there is one.',
            }),
        }


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
