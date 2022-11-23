from django.db import models
from django.conf import settings
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

KEY = settings.TELEGRAM_APIKEY_BOT

updater = Updater(KEY,use_context=True)

def start(update: Update,context: CallbackContext):
	update.message.reply_text('''Gracias por usar el bot de decide.
	Con este bot podrá consultar datos de las votaciones. Para más ayuda use el comando help''')

def help(update:Update,context:CallbackContext):
	update.message.reply_text('''El bot decide ofrece los siguientes comandos:
    /start: Inicia al bot
    /help: Mensaje de ayuda
	/getvotes: Genera un documento de los resultados de una votación
    /vote: Permite votar''')

def getvotes(update:Update,context:CallbackContext):
	# Display generated graphs?
    # https://docs.python-telegram-bot.org/en/v20.0a5/telegram.bot.html#telegram.Bot.send_poll
	pass

def vote(update:Update, context: CallbackContext):
   	# https://docs.python-telegram-bot.org/en/v20.0a5/telegram.bot.html#telegram.Bot.send_poll
    pass


def unknown(update:Update,context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el comando:'+
                             update.message.text)

def unknown_text(update:Update,context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el significado de:'+
                             update.message.text)

updater.dispatcher.add_handler(CommandHandler('start',start))
updater.dispatcher.add_handler(CommandHandler('help',help))
updater.dispatcher.add_handler(CommandHandler('getvotes',getvotes))
updater.dispatcher.add_handler(CommandHandler('vote',vote))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands
  
# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()