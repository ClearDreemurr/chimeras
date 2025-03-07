import random
import math

class Task:
    def __init__(self, completion=None, consumption=None):
        if completion is None and consumption is None:
            limit_attri = 18
            completion = random.randint(1, limit_attri)
            consumption = abs(limit_attri - completion + random.randint(-3, 1))
        self.completion = completion
        self.progress = 0
        self.consumption= consumption
        self.completed_chimera = None

    def do_progress(self, amount, gamestate):
        self.progress+=amount
    
    def turn_task(self, turn):
        if turn > 0:
            tasks=[]
            for i in range(5):
                tasks.append(Task(self.calc_completion(turn, i), self.calc_consumption(turn, i)))  
            return tasks
        else:
            print("轮次必须大于零，创建失败！")
      
    def calc_completion(self, turn, i):
        """
        >>> t = Task()
        >>> t.calc_completion(1, 0)
        7
        >>> t.calc_completion(7, 4)
        302
        >>> t.calc_completion(8, 0)
        168
        >>> t.calc_completion(10, 4)
        578
        >>> t.calc_completion(12, 2)
        394
        """
        if i == 4:
            return 5 * turn * turn + 7 * turn + 8
        return (5 * turn * turn + turn + 8) // 2 + turn * i
    
    def calc_consumption(self, turn, i):
        """
        >>> t = Task()
        >>> t.calc_consumption(1, 0)
        2
        >>> t.calc_consumption(1, 1)
        2
        >>> t.calc_consumption(1, 4)
        3
        >>> t.calc_consumption(2, 0)
        3
        >>> t.calc_consumption(2, 4)
        4
        """
        return turn + i // 4 + 1
    
    def is_completed(self):
        return self.progress >= self.completion