from django import forms

from .models import OfficeHour


class OfficeHourForm(forms.ModelForm):
    class Meta:
        model = OfficeHour
        fields = ['subject', 'weekday', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'end_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def __init__(self, *args, monitor, **kwargs):
        super().__init__(*args, **kwargs)
        # The monitor is set before validation, so OfficeHour.clean() can
        # check the subject and look for overlapping slots.
        self.instance.monitor = monitor
        self.fields['subject'].queryset = monitor.monitored_subjects.all()
