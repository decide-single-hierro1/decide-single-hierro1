from base.tests import BaseTestCase
from base import mods
from census.models import Census
from voting.models import Voting

from rest_framework.test import APIClient

import visualizer.metrics as metrics

class VisualizerTests(BaseTestCase):
    data = ['visualizer/migrations/prueba.json',]

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_vista_visualizer(self):
       response = self.client.get('/visualizer/')
       self.assertEqual(response.status_code, 200)