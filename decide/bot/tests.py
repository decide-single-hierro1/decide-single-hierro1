from django.test import TestCase
import bot.bot
import asyncio


class SimpleTest(TestCase):
	def test_on_ready(self):
		a = bot.bot.on_ready()
		self.assertIsNotNone(a)
	def test_on_message_list(self):
		a = bot.bot.on_message('$list')
		self.assertIsNotNone(a)
	def test_on_message_votes(self):
		a = bot.bot.on_message('$votes')
		self.assertIsNotNone(a)
	def test_on_message_started(self):
                a = bot.bot.on_message('$started')
                self.assertIsNotNone(a)


