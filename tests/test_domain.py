import base64, io, json, math, unittest
import numpy as np
from lab.core import astar, clean
from lab import audio

class CoreTests(unittest.TestCase):

    def test_astar_routes_around_wall(self):
        path = astar([0, 0], [4, 4], [[2, y] for y in range(4)], 5)
        self.assertEqual(path[-1], [4, 4])
        self.assertTrue(all((p[0] != 2 or p[1] == 4 for p in path)))

    def test_astar_impossible(self):
        self.assertEqual(astar([0, 0], [2, 2], [[1, y] for y in range(3)], 3), [])

    def test_json_serialization(self):
        self.assertEqual(clean({'a': np.int64(2), 'b': float('nan')}), {'a': 2, 'b': None})

class AudioTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = audio.Engine()

    def test_finite_features(self):
        self.assertTrue(np.isfinite(self.engine.features(*self.engine.signal(8))[0]).all())

    def test_audio_round_trip(self):
        e = self.engine
        e.sample({'kind': 'normal'})
        self.assertEqual(e.state['last_audio']['sample_rate'], 8000)
        self.assertEqual(len(e.state['last_audio']['bands']), 24)

    def test_bad_file_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.analyze({'data': base64.b64encode(b'not a wave').decode()})
