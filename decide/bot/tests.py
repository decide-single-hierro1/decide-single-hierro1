from django.test import TestCase
import bot.bot
import asyncio
import pytest
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.models import Auth
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from voting.models import Voting, Question, QuestionOption
from . import telegrambot, observer

from unittest.mock import Mock


class SimpleTest(TestCase):

    	def create_voting(self):
        	q = Question(desc='test question')
        	q.save()
        	for i in range(5):
            		opt = QuestionOption(question=q, option='option {}'.format(i+1))
            		opt.save()
        	v = Voting(name='test voting', question=q)
        	v.save()

        	a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        	a.save()
        	v.auths.add(a)

        	return v

    	def create_voters(self, v, n=11):
        	for i in range(n):
            		u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            		u.is_active = True
            		u.save()
            		c = Census(voter_id=u.id, voting_id=v.id)
            		c.save()

    	def get_or_create_user(self, pk):
        	user, _ = User.objects.get_or_create(pk=pk)
        	user.username = 'user{}'.format(pk)
        	user.set_password('qwerty')
        	user.save()
        	return user

    	def store_votes(self, v):
        	voters = list(Census.objects.filter(voting_id=v.id))
        	voter = voters.pop()

        	clear = {}
        	for opt in v.question.options.all():
            		clear[opt.number] = 0
            		for _ in range(2):
                		a, b = self.encrypt_msg(opt.number, v)
                		data = {
                    			'voting': v.id,
                    			'voter': voter.voter_id,
                    			'vote': { 'a': a, 'b': b },
                		}
                		clear[opt.number] += 1
                		user = self.get_or_create_user(voter.voter_id)
                		self.login(user=user.username)
                		voter = voters.pop()
                		mods.post('store', json=data)
        	return clear

	def complete_voting(self):
        	v = self.create_voting()
        	self.create_voters(v)

        	v.create_pubkey()
        	v.start_date = timezone.now()
        	v.save()

        	self.store_votes(v)

        	self.login()  # set token
       		v.tally_votes(self.token)

       	 	return v

    	def test_on_ready(self):
		a = bot.bot.on_ready()
		self.assertIsNotNone(a)

    	def test_on_message_list(self):
		a = bot.bot.on_message('$list') 
		self.assertIsNotNone(a)


