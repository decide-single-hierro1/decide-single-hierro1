from base.tests import BaseTestCase
import visualizer.metrics as metrics

class VisualizerTests(BaseTestCase):
    # data = ['visualizer/migrations/prueba.json', ]
    
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
        
    def test_vista_visualizer(self):
       response = self.client.get('/visualizer/')
       self.assertEqual(response.status_code, 200)

    def test_votacion_existente(self):
        response = self.client.get('/visualizer/1/')
        self.assertEqual(response.status_code, 200)

    def test_votacion_no_existente(self):
        response = self.client.get('/visualizer/999/')
        self.assertEqual(response.status_code, 404)
        
    def test_num_votos(self):
        num = metrics.votesOfVoting(1)
        res = 3
        self.assertEqual(res, num)

    def test_abstenciones(self):
        res = 1
        abstenciones = metrics.abstentions(1)
        self.assertEquals(res, abstenciones)

    def test_votaciones_no_empezadas(self):
        res = 1
        num = metrics.unstartedVotings()
        self.assertEquals(res, num)

    def test_votaciones_empezadas(self):
        res = 4
        num = metrics.startedVotings()
        self.assertEquals(res, num)

    def test_votaciones_terminadas(self):
        res = 2
        num = metrics.finishedVotings()
        self.assertEquals(res, num)

    def test_votaciones_cerradas(self):
        res = 2
        num = metrics.closedVotings()
        self.assertEquals(res, num)

    def test_comparador(self):
        res = 150
        comp = metrics.votingComparator(1,2)
        self.assertEquals(res, comp)
