import random
import math

class Task:
    def __init__(self):
        limit_attri = 18
        completion = random.randint(1, limit_attri)
        consumption = abs(limit_attri - completion + random.randint(-3, 1))
        self.completion = completion
        self.progress = 0
        self.consumption= consumption
        self.completed_chimera = None

    def __init__(self, completion=None, consumption=None):
        if completion is None:
            limit_attri = 18
            completion = random.randint(1, limit_attri)
            consumption = abs(limit_attri - completion + random.randint(-3, 1))
        self.completion = completion
        self.progress = 0
        self.consumption= consumption
        self.completed_chimera = None
    
    def is_completed(self):
        return self.progress >= self.completion