from store.models import Vote  
from voting.models import Voting, Question
from census.models import Census
from django.shortcuts import get_list_or_404

def listVotes():
    return Vote.objects.all()

def votesOfVoting(v_id):
    return Vote.objects.filter(voting_id = v_id).count()

def unstartedVotings():
    return Voting.objects.filter(start_date__isnull=True).count()

def startedVotings():
    return Voting.objects.filter(start_date__isnull=False).count()

def finishedVotings():
    return Voting.objects.filter(end_date__isnull=False, tally__isnull=False).count()

def closedVotings():
    return Voting.objects.filter(end_date__isnull=False, tally__isnull=True).count()

def votingComparator(v1_id, v2_id):
    v1 = votesOfVoting(v1_id)
    v2 = votesOfVoting(v2_id)
    return (v1/v2)*100

def abstentions(v_id):
    v = votesOfVoting(v_id)
    c = Census.objects.filter(voting_id = v_id).count()
    return c - v
