from django.test import TestCase

import bot
class testBot(TestCase):
	def log(self):
		a =   bot.on_ready()
		self.assertEqual(a.status_code, 200)
