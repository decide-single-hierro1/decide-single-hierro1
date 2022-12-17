from base.tests import BaseTestCase
from base import mods
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
import visualizer.metrics as metrics

from rest_framework.test import APIClient

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

class VisualizerTests(BaseTestCase):
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
        v = Voting( name='test voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def create_voters(self, v,):
        for i in range(100):
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

    def store_votes(self, v,rang):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(rang):
                a, b = self.encrypt_msg(opt.number, v)
                print(str(i))
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

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None
        super().tearDown()

    def test_vista_visualizer(self):
        response = self.client.get('/visualizer/')
        self.assertEqual(response.status_code, 200)

    def test_votacion_existente(self):
        v = self.create_voting()
        response = self.client.get('/visualizer/'+str(v.id)+'/')
        self.assertEqual(response.status_code, 200)

    def test_votacion_no_existente(self):
        response = self.client.get('/visualizer/999/')
        self.assertEqual(response.status_code, 404)

    def test_vista_detalle(self):
        v = self.create_voting()
        response=self.client.get('/visualizer/' +str(v.id)+'/')
        self.assertEqual(response.status_code,200)
    def test_vista_detalle_Neg(self):
        response=self.client.get('/visualizer/-1/')
        self.assertEqual(response.status_code,404)
    def test_vista_detalle_IdNoExiste(self):
        v = self.create_voting()
        response=self.client.get('/visualizer/100/')
        self.assertEqual(response.status_code,404) 

    def test_num_votos(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        self.store_votes(v,5)
        num = metrics.votesOfVoting(v.id)
        res = 25
        self.assertEqual(res, num)
    
    def test_abstenciones(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        self.store_votes(v,5)
        res = 75
        abstenciones = metrics.abstentions(v.id)
        self.assertEquals(res, abstenciones)

    def test_votaciones_no_empezadas(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        self.create_voting()
        res = 1
        num = metrics.unstartedVotings()
        self.assertEquals(res, num)

    def test_votaciones_empezadas(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        v1 = self.create_voting()
        self.create_voters(v1)
        v1.create_pubkey()
        v1.start_date = timezone.now()
        v1.save()

        v2 = self.create_voting()
        self.create_voters(v2)
        v2.create_pubkey()
        v2.start_date = timezone.now()
        v2.save()

        v3 = self.create_voting()
        self.create_voters(v3)
        v3.create_pubkey()
        v3.start_date = timezone.now()
        v3.save()

        self.create_voting()
        self.create_voting()
        self.create_voting()

        res = 4
        num = metrics.startedVotings()
        self.assertEquals(res, num)
        
    def test_comparador(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        self.store_votes(v,5)

        v1 = self.create_voting()
        self.create_voters(v1)
        v1.create_pubkey()
        v1.start_date = timezone.now()
        v1.save()
        self.store_votes(v1,4)
        print(str(v.id)+': votos ->'+ str(metrics.votesOfVoting(v.id)) + str(v1.id)+': votos ->'+ str(metrics.votesOfVoting(v1.id)))
        res = 125
        comp = metrics.votingComparator(v.id,v1.id)
        self.assertEquals(res, comp)

    def test_votaciones_cerradas(self):
        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.end_date = timezone.now()
        v.tally = None
        v.save()

        v1 = self.create_voting()
        self.create_voters(v1)
        v1.create_pubkey()
        v1.start_date = timezone.now()
        v1.end_date = timezone.now()
        v1.tally = None
        v1.save()
        res = 2
        num = metrics.closedVotings()
        self.assertEquals(res, num)
        

    def test_votaciones_finalizadas(self):

        v = self.create_voting()
        self.create_voters(v)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.end_date = timezone.now()
        v.save()
        self.store_votes(v,5)
        user_admin = User(username='admin', is_staff=True)
        user_admin.set_password('qwerty')
        user_admin.save()
        self.login('admin', 'qwerty')  # set token
        v.tally_votes(self.token)
        v.tally=[2]
        res = 1
        num = metrics.finishedVotings()
        self.assertEquals(res, num)

        