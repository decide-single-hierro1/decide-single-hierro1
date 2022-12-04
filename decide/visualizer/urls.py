from django.urls import path
from .views import VisualizerView, VisualizerQuestion,  VisualizerAll


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('',VisualizerAll.as_view()),
    path('question/<int:question_id>/',VisualizerQuestion.as_view()),
]
