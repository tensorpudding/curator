import unittest
import random

from curator import queue 

class RandomQueueTest(unittest.TestCase):

    def test_derangement(self):
        self.queue = queue.RandomQueue(range(1,200))
        self.assertNotEqual(self.queue.sort(), self.queue)
        self.assertEqual(set(range(1,200)), set(self.queue))
