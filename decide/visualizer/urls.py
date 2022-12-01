from django.urls import path
from .views import VisualizerView, VisualizerQuestion,  VisualizerAll
from .metrics import listVotes, votesOfVoting, unstartedVotings, startedVotings, finishedVotings, closedVotings, votingComparator, abstentions


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('',VisualizerAll.as_view()),
    path('question/<int:question_id>/',VisualizerQuestion.as_view()),
    path('list', listVotes),
    path('votes', votesOfVoting),
    path('unstarted', unstartedVotings),
    path('started', startedVotings),
    path('finished', finishedVotings),
    path('closed', closedVotings),
    path('comparator/<int:v1_id>/<int:v2_id>', votingComparator),
    path('abstentions/<int:v_id>', abstentions),
]
