from django.core.management.base import BaseCommand
from telegram_bot import bot


class Command(BaseCommand):
    help = 'Runs telegram bot dispatcher'
    
    def handle(self, *args, **options):
        bot.startBot()