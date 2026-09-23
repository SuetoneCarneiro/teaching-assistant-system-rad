from django.urls import path

from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='list'),
    path('new/', views.QuestionCreateView.as_view(), name='create'),
    path('knowledge/', views.knowledge_base, name='knowledge_base'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/claim/', views.claim_question, name='claim'),
    path('<int:pk>/answer/', views.AnswerView.as_view(), name='answer'),
    path('<int:pk>/close/', views.close_question, name='close'),
]
