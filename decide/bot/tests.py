from django.test import TestCase
import bot
class SimpleTest(TestCase):
	async def test_on_ready(self):
		a = await bot.on_ready()
		self.assertEqual(a, 200)
	async def test_on_message_list(self):
		a=await bot.on_message('$list')
		self.assertEquals(a,404)
