from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .roles import STUDENTS_GROUP


class SignUpView(CreateView):
    """RF2: public signup. New accounts join the Students group and get
    nothing else: no extra permissions, is_staff stays False."""

    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('questions:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        students, _ = Group.objects.get_or_create(name=STUDENTS_GROUP)
        self.object.groups.add(students)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome, {self.object.username}! Your account was created.')
        return response
