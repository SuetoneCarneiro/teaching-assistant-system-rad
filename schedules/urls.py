from django.urls import path

from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.MyOfficeHoursView.as_view(), name='mine'),
]
