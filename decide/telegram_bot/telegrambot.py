from django.conf import settings
from django.http import Http404

from base import mods
from visualizer import metrics, plots
from telegram_bot import observer

from django_telegrambot.apps import DjangoTelegramBot

from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import logging
import os

logger = logging.getLogger(__name__)

KEY = settings.TELEGRAM_APIKEY_BOT

def main():
    dp = DjangoTelegramBot.dispatcher
    events = observer.event_handler()
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('getVotingInfo', getVotingInfo))
    dp.add_handler(CommandHandler('getVotingPlot', getVotingPlot))
    dp.add_handler(CommandHandler('getAllVotingsInfo', getAllVotingsInfo))
    dp.add_handler(CommandHandler('getAllVotingsPlot', getAllVotingsPlot))
    dp.add_handler(CommandHandler('listVotings', listVotings))
    dp.add_handler(CommandHandler('subscribe', events.subscribe))
    dp.add_handler(CommandHandler('un-subscribe', events.unsubscribe))
    dp.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands
    
    dp.add_handler(MessageHandler(Filters.text, unknown_text)) # Filters out unknown messages.

    dp.add_error_handler(error) # Error handler

def start(update: Update, context:CallbackContext):
	update.message.reply_text(
        'Gracias por usar el bot de decide.\n'
        'Con este bot podrá consultar datos de las votaciones. Para más ayuda use el comando /help'
    )

def help(update:Update, context:CallbackContext):
    update.message.reply_text(
        'El bot decide ofrece los siguientes comandos:\n'
        '   /start: Inicia al bot\n'
        '   /help: Mensaje de ayuda\n'
        '   /getVotingInfo <id>: Muestra la información de una votación\n'
        '   /getVotingPlot <id>: Muestra la información de una votación en un gráfico\n'
        '   /getAllVotingsInfo: Muestra informacion general sobre todas las votaciones\n'
        '   /getAllVotingsPlot: Muestra informacion general sobre todas las votaciones en un gráfico\n'
        '   /listVotings: Lista todas las votaciones\n'
    )    

def getVotingInfo(update:Update, context:CallbackContext):
   
    try:
        vid = context.args[0]
        voting = mods.get('voting', params={'id': vid})[0]
        name = voting['name']
        desc = voting['desc']

        votes = metrics.votesOfVoting(vid)
        abstentions = metrics.abstentions(vid)

        re = f'Información de la votación {vid}\n'
        re += f'Nombre: {name}\n'
        if (desc == '' or desc == None):
            re += 'Descripción: Esta votación no tiene descripción\n'
        else:
            re += f'Descripción: {desc}\n'
            
        re += f'Número de votos: {votes}\n'
        re += f'Número de abstenciones: {abstentions}\n'

        update.message.reply_text(re)
    except:
        raise Http404
        
def getVotingPlot(update:Update, context:CallbackContext):
    
    figFile = 'fig.png'
    
    try:
        vid = context.args[0]
        voting = mods.get('voting', params={'id': vid})[0]

        if voting['postproc'] == None:
            update.message.reply_text('Gráficos no disponibles; el recuento no se ha realizado todavía')
            return

        names = []
        res = []
        total = 0

        for opt in voting['postproc']:
            names.append(opt['option'])
            res.append(opt['votes'])
            total += int(opt['votes'])
        names.append('abstenciones')
        res.append(metrics.abstentions(vid))
        total += metrics.abstentions(vid)
        resPercent = [i/total for i in res]

        plots.votingBarPlot(figFile, names, res)
        update.message.reply_photo(open(figFile, 'rb'))
        plots.votingPieChart(figFile, names, resPercent)
        update.message.reply_photo(open(figFile, 'rb'))
    except:
        raise Http404
    
    # Clean file
    if os.path.exists(figFile):
        os.remove(figFile)
        
def getAllVotingsInfo(update:Update, context:CallbackContext):
    try:
        unstarted = metrics.unstartedVotings()
        started = metrics.startedVotings()
        finished = metrics.finishedVotings()
        closed = metrics.closedVotings()
        update.message.reply_text(
            f'Información general\n'
            f'Votaciones por compenzar: {unstarted}\n'
            f'Votaciones en curso: {started}\n'
            f'Votaciones finalizadas: {finished}\n'
            f'Votaciones cerradas: {closed}\n'
        )
    except:
        raise Http404
        
def getAllVotingsPlot(update:Update, context:CallbackContext):
    figFile = 'fig.png'
    
    try:
        plots.votingBarPlotAll(figFile)
        update.message.reply_photo(open(figFile, 'rb'))
        plots.votingPieChartAll(figFile)
        update.message.reply_photo(open(figFile, 'rb'))
    except:
        raise Http404

    # Clean file
    if os.path.exists(figFile):
        os.remove(figFile)

def listVotings(update:Update, context:CallbackContext):
    try:
        votingsList = metrics.listVotings()
        re = ''
        for voting in votingsList:
            re += f'Id de la votación {voting.id}\n'
            if (voting.desc == '' or voting.desc == None):
                re += 'Descripción: Esta votación no tiene descripción\n'
            else:
                re += f'Descripción: {voting.desc}\n'
            re += '\n'
        update.message.reply_text(re)
    except:
        raise Http404

def unknown(update:Update, context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el comando: '+
                             update.message.text)

def unknown_text(update:Update, context:CallbackContext):
	update.message.reply_text('Lo siento, no reconozco el significado de: '+
                             update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
