from django.core.management.base import BaseCommand
from decide.telegram_bot import telegrambot


class Command(BaseCommand):
    help = 'Runs telegram bot dispatcher'
    
    def handle(self, *args, **options):
        telegrambot.main()