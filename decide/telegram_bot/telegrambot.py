from django.conf import settings
from django.http import Http404

from base import mods
from telegram_bot import observer

from django_telegrambot.apps import DjangoTelegramBot

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import logging
logger = logging.getLogger(__name__)

KEY = settings.TELEGRAM_APIKEY_BOT

def main():
    dp = DjangoTelegramBot.dispatcher
    events = observer.event_handler()
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('getvotes', getvotes))
    dp.add_handler(CommandHandler('subscribe',events.subscribe))
    dp.add_handler(CommandHandler('un-subscribe',events.unsubscribe))
    dp.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands
    
    dp.add_handler(MessageHandler(Filters.text, unknown_text)) # Filters out unknown messages.

    dp.add_error_handler(error) # Error handler


def start(update: Update,context: CallbackContext):
	update.message.reply_text('''Gracias por usar el bot de decide.
	Con este bot podrá consultar datos de las votaciones. Para más ayuda use el comando help''')

def help(update:Update,context:CallbackContext):
	update.message.reply_text('''El bot decide ofrece los siguientes comandos:
    /start: Inicia al bot
    /help: Mensaje de ayuda
	/getvotes [voting_id]: Genera un documento de los resultados de una votación dada
    /subscribe [voting_id]: El usuario se subscribe a una votación en curso. Se le notificará cuando termine del resultado
    /un-subscribe [voting_id]: El usuario es borrado de la lista de notificados de la votación''')
    

def getvotes(update:Update,context:CallbackContext):
	# Display generated graphs?
    
    try:
        vid = context.args[0]
        r = mods.get('voting', params={'id': vid})
        if len(r) == 0:
            update.message.reply_text("No se encontró una votación para los datos suministrados.")
        update.message.reply_text(r)
    except:
        raise Http404

def unknown(update:Update,context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el comando:'+
                             update.message.text)

def unknown_text(update:Update,context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el significado de:'+
                             update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

