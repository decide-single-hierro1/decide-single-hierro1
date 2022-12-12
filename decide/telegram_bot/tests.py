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
from . import telegrambot

from unittest.mock import Mock

class TelegramBotTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        telegrambot.main()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
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

    def test_start(self):
        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.start(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with(
            'Gracias por usar el bot de decide.\n'
            'Con este bot podrá consultar datos de las votaciones. Para más ayuda use el comando /help'
        )

    def test_help(self):
        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.help(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with(
            'El bot decide ofrece los siguientes comandos:\n'
            '   /start: Inicia al bot\n'
            '   /help: Mensaje de ayuda\n'
            '   /getVotingInfo <id>: Muestra la información de una votación\n'
            '   /getVotingPlot <id>: Muestra la información de una votación en un gráfico\n'
            '   /getAllVotingsInfo: Muestra informacion general sobre todas las votaciones\n'
            '   /getAllVotingsPlot: Muestra informacion general sobre todas las votaciones en un gráfico\n'
            '   /listVotings: Lista todas las votaciones\n'
        )

    def test_getVotingInfo(self):
        # Create Voting with votes
        v = self.complete_voting()
        
        mocked_update = Mock()
        mocked_context = Mock()

        mocked_context.args = [v.id]

        telegrambot.getVotingInfo(mocked_update, mocked_context)
        
        mocked_update.message.reply_text.assert_called_with(
            f'Información de la votación {v.id}\n'
            'Nombre: test voting\n'
            'Descripción: Esta votación no tiene descripción\n'
            'Número de votos: 10\n'
            'Número de abstenciones: 1\n'
        )

    def test_getVotingPlot(self):
        # Create Voting
        v = self.create_voting()

        # Start Voting
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        mocked_update = Mock()
        mocked_context = Mock()

        mocked_context.args = [v.id]

        telegrambot.getVotingPlot(mocked_update, mocked_context)
        mocked_update.message.reply_text.assert_called_with('Gráficos no disponibles; el recuento no se ha realizado todavía')

        mocked_update = Mock()
        mocked_context = Mock()

        # Create Voting with votes
        v2 = self.complete_voting()
        mocked_context.args = [v2.id]

        telegrambot.getVotingPlot(mocked_update, mocked_context)

    def test_getAllVotingsInfo(self):
        # Create Voting
        v = self.create_voting()

        # Start Voting
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.getAllVotingsInfo(mocked_update, mocked_context)

        # Test Voting is displayed as ongoing
        mocked_update.message.reply_text.assert_called_with(
            'Información general\n'
            'Votaciones por compenzar: 0\n'
            'Votaciones en curso: 1\n'
            'Votaciones finalizadas: 0\n'
            'Votaciones cerradas: 0\n'
        )

        # Close Voting
        v.end_date = timezone.now()
        v.save()

        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.getAllVotingsInfo(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with(
            'Información general\n'
            'Votaciones por compenzar: 0\n'
            'Votaciones en curso: 0\n'
            'Votaciones finalizadas: 0\n'
            'Votaciones cerradas: 1\n'
        )

    def test_getAllVotingsPlot(self):
        # Create Votings
        v = self.create_voting()
        v2 = self.create_voting()

        # Start Voting
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.getAllVotingsPlot(mocked_update, mocked_context)

    def test_listVotings(self):
        # Create Votings
        v = self.create_voting()
        v2 = self.create_voting()

        mocked_update = Mock()
        mocked_context = Mock()

        telegrambot.listVotings(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with(
            f'Id de la votación {v.id}\n'
            'Descripción: Esta votación no tiene descripción\n'
            '\n'
            f'Id de la votación {v2.id}\n'
            'Descripción: Esta votación no tiene descripción\n'
            '\n'
        )

    def test_unknown(self):
        mocked_update = Mock()
        mocked_context = Mock()
        mocked_update.message.text = '/testUnknown'

        telegrambot.unknown(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with('Lo siento, no reconozco el comando: /testUnknown')

    def test_unknownText(self):
        mocked_update = Mock()
        mocked_context = Mock()
        mocked_update.message.text = 'test unknown text'

        telegrambot.unknown_text(mocked_update, mocked_context)

        mocked_update.message.reply_text.assert_called_with('Lo siento, no reconozco el significado de: test unknown text')

