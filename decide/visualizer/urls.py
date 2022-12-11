from django.urls import path
from .views import *
urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('',VisualizerAll.as_view()),
    path('question/<int:question_id>/',VisualizerQuestion.as_view()),
    path('list', VisualizerList.as_view()),
    path('votes/<int:v_id>', VotesOfVoting.as_view()),
    path('unstarted', UnstartedVotings.as_view()),
    path('started', StartedVotings.as_view()),
    path('finished', FinishedVotings.as_view()),
    path('closed', ClosedVotings.as_view()),
    path('comparator/<int:v1_id>/<int:v2_id>', VotingComparator.as_view()),
    path('abstentions/<int:v_id>', Abstentions.as_view()),
]
