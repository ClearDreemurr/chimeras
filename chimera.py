import random
import math

class Chimera:

    def __init__(self, name, energy, efficiency):
        self.name = name
        self.energy = energy
        self.efficiency = efficiency

    def action(self, gamestate, phase):
        if phase == 'prepare':
            self.prepare_action(gamestate)
        elif phase == 'work':
            self.work_action(gamestate)
        elif phase == 'settle':
            self.settlement_action(gamestate)

    def prepare_action(self, gamestate):
        self.skills()

    def work_action(self, gamestate):
        """
        >>> import task, gamestate
        >>> chimeras = [Chimera("请假王", 5, 10)]
        >>> tasks = [task.Task(5, 2)]
        >>> gamestate = gamestate.GameState(chimeras, tasks)
        >>> tasks[0].progress
        0
        >>> chimeras[0].energy
        5
        >>> chimeras[0].work_action(gamestate)
        >>> tasks[0].progress
        10
        >>> chimeras[0].energy
        3
        >>> tasks[0].is_completed()
        True
        >>> tasks[0].completed_chimera is chimeras[0]
        True
        """
        gamestate.tasks[0].progress += self.efficiency
        self.energy -= gamestate.tasks[0].consumption
        if gamestate.tasks[0].is_completed():
            gamestate.tasks[0].completed_chimera = self

    def settlement_action(self, gamestate):
        self.skills()

    def skills(self):
        pass

    def is_alive(self):
        return self.energy > 0
    
class NormalChimera(Chimera):
    def __init__(self):
        limit_attri = 10
        energy = random.randint(1, limit_attri)
        efficiency = abs(limit_attri - energy + random.randint(-3, 1))

        # 根据属性的总和或者单个属性的高低选择名称：
        if energy <= limit_attri / 3:
            name_list = ["最效率"]
        elif energy <= limit_attri * 2 / 3:
            name_list = ["最社畜"]
        else:
            name_list = ["最老实"]
        name = random.choice(name_list)
        super().__init__(name, energy, efficiency)