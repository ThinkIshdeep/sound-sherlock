"""A/B playback must never refer to an overwritten recording."""
import unittest
from pathlib import Path
from lab.audio import Engine
from lab.core import RUNTIME

class RecordingFilesTest(unittest.TestCase):
    def test_generated_pair_keeps_distinct_immutable_wavs(self):
        engine = Engine()
        first = engine.sample({'kind': 'normal'})
        first_path = RUNTIME / first['audio_url'].removeprefix('/')
        original = first_path.read_bytes()
        second = engine.sample({'kind': 'anomaly'})
        second_path = RUNTIME / second['audio_url'].removeprefix('/')
        self.assertNotEqual(first_path, second_path)
        self.assertEqual(first_path.read_bytes(), original)
        self.assertNotEqual(original, second_path.read_bytes())
        self.assertEqual(engine.state['history'][0]['audio_url'], first['audio_url'])
        first_path.unlink()
        second_path.unlink()
