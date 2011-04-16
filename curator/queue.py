import random

class RandomQueue(list):

    def __init__(self, list):
        random.shuffle(list)
        super(RandomQueue, self).__init__(list)
