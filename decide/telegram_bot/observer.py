import telegram_bot
from django.http import Http404

from base import mods

from telegram.bot import Bot
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext

class telegramObserver():

    def __init__(self,**kwargs):
        self.chatId = kwargs.get('id')
        self.subscriptionId = kwargs.get('vid')

    def update(self):
        try:
            r = mods.get('voting', params={'id': self.subscriptionId})
            if len(r) == 0:
                Bot.send_message(chat_id=self.chatId,text=r)
        except:
            raise Http404


class votingSubject():
    #subscriber = [chatId]
    def __init__(self,id):
        self.id = id
        self.__subscribers: list[telegramObserver] = []

    def attach(self, observer:telegramObserver):
        self.__subscribers.append(observer)
    
    def dettach(self,observer:telegramObserver):
        self.__subscribers.remove(observer)

    def notify(self):
        for observer in self.__subscribers:
            observer.update()

class event_handler():
    def __init__(self) -> None:
        self.list_events:list[votingSubject] = []

    def subscribe(self,update:Update,context:CallbackContext):
        try:
            vid = context.args[0]
            observer = telegramObserver(id=update.message.chat.id(),vid=vid)
            subject = next((x.id == vid for x in self.list_events),votingSubject(vid))
            subject.attach(observer)
            if not any(x.id == vid for x in self.list_events):
                self.list_events.append(subject)
            update.message.reply_text('Subscripción realizada con éxito. Espere hasta que finalice la votación para consultar los resultados')
        except:
            update.message.reply_text('Algo ha fallado')


    def unsubscribe(self,update:Update,context:CallbackContext):
        try:
            vid = context.args[0]
            subject:votingSubject = next(x.id == vid for x in self.list_events)
            observer:telegramObserver = next(x.chatId == update.message.chat.id for x in subject)
            subject.dettach(observer)
            update.message.reply_text('Subscripción anulada. Ya no recibirá un mensaje al finalizar la votación')
        except:
            update.message.reply_text('Algo ha fallado')
