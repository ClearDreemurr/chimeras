import random
import math

class Chimera:
    def __init__(self, name, efficiency, energy):
        self.name = name
        self.efficiency = efficiency
        self.energy = energy
        self.place = None

    def action(self, gamestate, phase):
        if phase == 'prepare':
            self.prepare_action(gamestate)
        elif phase == 'work':
            self.work_action(gamestate)
        elif phase == 'addition':
            return self.additional_action(gamestate)
        elif phase == 'settle':
            self.settlement_action(gamestate)

    def prepare_action(self, gamestate):
        pass

    def work_action(self, gamestate):
        """
        >>> import task, gamestate
        >>> chimeras = [Chimera("请假王", 10, 5)]
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
        self.reduce_energy(gamestate.tasks[0].consumption, gamestate)
        if gamestate.tasks[0].is_completed():
            gamestate.tasks[0].completed_chimera = self

    def additional_action(self, gamestate):
        return False

    def settlement_action(self, gamestate):
        pass

    def skill(self):
        pass

    def is_alive(self):
        return self.energy > 0
    
    def reduce_energy(self, amount, gamestate):
        self.energy -= amount

    def debut(self, gamestate):#why????
        pass

class NormalChimera(Chimera):
    nameset = ["摸鱼仔3 2", "压力怪5 3", "小坏蛋3 5", "真老实1 16", "负能量7 2"]
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
            name_list = ["真老实"]
        name = random.choice(name_list)
        super().__init__(name, efficiency, energy)

class RatRaceKing(Chimera):
    def __init__(self, name="内卷王", efficiency=3, energy=8):
        super().__init__(name, efficiency, energy)

    def settlement_action(self, gamestate):
        if gamestate.tasks[0].completed_chimera is self:
            self.energy += 3
            self.efficiency += 2

class BadTempered(Chimera):
    def __init__(self, name="坏脾气", efficiency=2, energy=9):
        super().__init__(name, efficiency, energy)

    def reduce_energy(self, amount, gamestate):
        """
        >>> from task import *
        >>> from gamestate import *
        >>> gs = GameState([BadTempered(), Chimera("aa", 5, 10)], [Task(20, 1)])
        >>> gs.place[1].chimera.energy
        10
        >>> gs.update()
        >>> gs.place[1].chimera.energy
        9
        """
        super().reduce_energy(amount, gamestate)
        if self.place.next.chimera:
            self.place.next.chimera.reduce_energy(1, gamestate)

class ToughCookie(Chimera):
    def __init__(self, name='抗压包', efficiency=2, energy=5):
        super().__init__(name, efficiency, energy)

    def reduce_energy(self, amount, gamestate):
        """
        >>> from task import *
        >>> from gamestate import *
        >>> gs = GameState([BadTempered(), ToughCookie(), Chimera("aa", 5, 10)], [Task(20, 1)])
        >>> gs.place[0].chimera.efficiency
        2
        >>> gs.place[2].chimera.efficiency
        5
        >>> gs.update()
        >>> gs.place[1].chimera.energy
        4
        >>> gs.place[0].chimera.efficiency
        3
        >>> gs.place[2].chimera.efficiency
        6
        """
        super().reduce_energy(amount, gamestate)
        if self.place.next.chimera:
            self.place.next.chimera.efficiency+=1
        if self.place.last.chimera:
            self.place.last.chimera.efficiency+=1

class AbsenteeFreak(Chimera):
    def __init__(self, name="请假狂", efficiency=2, energy=7):
        super().__init__(name, efficiency, energy)

    def reduce_energy(self, amount, gamestate):
        """
        >>> from task import *
        >>> from gamestate import *
        >>> gs = GameState([BadTempered(), AbsenteeFreak(), Chimera("aa", 5, 10)], [Task(20, 1)])
        >>> gs.place[1].chimera.name
        '请假狂'
        >>> gs.place[1].chimera.efficiency
        2
        >>> gs.place[2].chimera.name
        'aa'
        >>> gs.update()
        >>> gs.place[1].chimera.name
        'aa'
        >>> gs.place[2].chimera.name
        '请假狂'
        >>> gs.place[2].chimera.efficiency
        4
        
        """
        super().reduce_energy(amount, gamestate)
        if self.place.next.chimera:
            self.efficiency += 2
            gamestate.swap(self, self.place.next.chimera)

class AbsenteeMaster(Chimera):
    def __init__(self, name='请假王', efficiency=6, energy=3):
        super().__init__(name, efficiency, energy)

    def reduce_energy(self, amount, gamestate):
        """
        >>> from task import *
        >>> from gamestate import *
        >>> gs = GameState([BadTempered(), AbsenteeMaster(), Chimera("aa", 5, 10)], [Task(20, 1)])
        >>> gs.place[1].chimera.name
        '请假王'
        >>> gs.place[1].chimera.energy
        3
        >>> gs.place[2].chimera.name
        'aa'
        >>> gs.update()
        >>> gs.place[1].chimera.name
        'aa'
        >>> gs.place[2].chimera.name
        '请假王'
        >>> gs.place[2].chimera.energy
        5
        """
        super().reduce_energy(amount, gamestate)
        if self.place.next.chimera:
            self.energy += 3
            gamestate.swap(self, self.place.next.chimera)

class Onlooker(Chimera):
    def __init__(self, name='看乐子', efficiency=3, energy=3):
        super().__init__(name, efficiency, energy)
    
    def skill(self):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 0, 1), Chimera('bb', 0, 1), Onlooker()], [Task(20, 1)])
        >>> gs.place[2].chimera.name
        '看乐子'
        >>> gs.place[2].chimera.efficiency
        3
        >>> gs.update()
        >>> gs.place[2].chimera
        >>> gs.place[1].chimera.name
        '看乐子'
        >>> gs.place[1].chimera.efficiency
        5
        >>> gs.update()
        >>> gs.place[1].chimera
        >>> gs.place[0].chimera.name
        '看乐子'
        >>> gs.place[0].chimera.efficiency
        7
        >>> gs.place[0].chimera.energy
        7
        """
        self.energy += 2
        self.efficiency += 2

class Healer(Chimera):
    def __init__(self, name="治愈师", efficiency=2, energy=5):
        super().__init__(name, efficiency, energy)

    def prepare_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('bb', 0, 1), Healer()], [Task(20, 0)])
        >>> gs.place[0].chimera.energy
        1
        >>> gs.update()
        >>> gs.place[0].chimera.energy
        2
        """
        self.place.last.chimera.energy += 1

class Bucktaker(Chimera):
    def __init__(self, name="背锅侠", efficiency=3, energy=6):
        super().__init__(name, efficiency, energy)

    def foo():
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('bb', 0, 2), Bucktaker()], [Task(20, 4)])
        >>> gs.update()
        >>> gs.place[0].chimera.energy
        8
        >>> gs.place[0].chimera.name
        'bb'
        >>> gs.place[1].chimera is None
        True
        """
        return

class SmallGroup(Chimera):
    def __init__(self, name="小团体", efficiency=3, energy=3):
        super().__init__(name, efficiency, energy)

    def prepare_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Chimera('bb', 5, 5), Chimera('cc', 4, 4), SmallGroup(), Chimera('dd', 2, 2) ], [Task(20, 0)])
        >>> [(p.chimera.efficiency, p.chimera.energy) for p in gs.place]
        [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2)]
        >>> gs.update()
        >>> [(p.chimera.efficiency, p.chimera.energy) for p in gs.place]
        [(6, 5), (6, 5), (5, 4), (3, 3), (2, 1)]
        """
        up = [self.place.last, self.place.last.last]
        for place in gamestate.place:
            if place in up:
                place.chimera.efficiency += 1
            elif place is not self.place:
                place.chimera.energy -= 1

class EmptyPromises(Chimera):
    def __init__(self, name="画饼王", efficiency=2, energy=7):
        super().__init__(name, efficiency, energy)

    def debut(self, gamestate):
        for place in gamestate.place:
            if place is not self.place and place.chimera:
                place.chimera.efficiency+=8
    
    def prepare_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([EmptyPromises(), Chimera('aa', 6, 6), Chimera('dd', 2, 2) ], [Task(20, 5)])
        >>> [p.chimera.efficiency for p in gs.place]
        [2, 14, 10]
        >>> gs.update()
        >>> [p.chimera.efficiency for p in gs.place]
        [2, 12, 8]
        >>> gs.update()
        >>> [p.chimera.efficiency for p in gs.place if p.chimera]
        [10, 6]
        """
        for place in gamestate.place:
            if place is not self.place and place.chimera:
                place.chimera.efficiency-=2

class WorkDitcher(Chimera):
    def __init__(self, name="跑路侠", efficiency=1, energy=1):
        super().__init__(name, efficiency, energy)

class Creditstealer(Chimera):
    def __init__(self, name="抢功劳", efficiency=15, energy=2):
        super().__init__(name, efficiency, energy)

    def additional_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Creditstealer()], [Task(20, 5)])
        >>> tmp = gs.tasks[0]
        >>> gs.update()
        >>> tmp.is_completed()
        True
        >>> tmp.completed_chimera is gs.place[1].chimera
        True
        >>> [p.chimera.energy for p in gs.place]
        [1, 2]
        """
        if self.efficiency >= gamestate.tasks[0].completion - gamestate.tasks[0].progress:
            gamestate.tasks[0].progress += self.efficiency
            if gamestate.tasks[0].completed_chimera is None:
                gamestate.tasks[0].completed_chimera = self
        return True

class Disservicer(Chimera):
    def __init__(self, name="帮倒忙", efficiency=-1, energy=5):
        super().__init__(name, efficiency, energy)
        
    def additional_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer()], [Task(20, 5)])
        >>> gs.update()
        >>> gs.tasks[0].progress
        5
        """
        gamestate.tasks[0].progress += self.efficiency
        if gamestate.tasks[0].completed_chimera is None and gamestate.tasks[0].completion < gamestate.tasks[0].progress:
            gamestate.tasks[0].completed_chimera = self
        return True

class KindPraiser(Chimera):
    def __init__(self, name="小夸夸", efficiency=3, energy=3):
        super().__init__(name, efficiency, energy)

    def praise(self, praised, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(),  Creditstealer()], [Task(20, 5)])
        >>> gs.update()
        >>> gs.place[1].chimera.efficiency
        -1
        >>> gs.place[3].chimera.efficiency
        17
        """
        if praised.efficiency >= 5:
            praised.efficiency += 2
    
class Workaholic(Chimera):
    def __init__(self, name="工作狂", efficiency=6, energy=10):
        super().__init__(name, efficiency, energy)

    #def additional_action(self, gamestate):
    #    """
    #    >>> from gamestate import *
    #    >>> from task import *
    #    >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(20, 5)])
    #    >>> tmp = gs.tasks[0]
    #    >>> gs.update()
    #    >>> gs.place[1].chimera.efficiency
    #    -1
    #    >>> gs.place[3].chimera.efficiency
    #    12
    #    >>> tmp.completed_chimera is gs.place[4].chimera
    #    True
    #    >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(7, 5)])
    #    >>> tmp = gs.tasks[0]
    #    >>> gs.update()
    #    >>> gs.place[1].chimera.efficiency
    #    -1
    #    >>> gs.place[3].chimera.efficiency
    #    12
    #    >>> tmp.completed_chimera is gs.place[3].chimera
    #    True
    #    """
    #    gamestate.tasks[0].progress += self.efficiency / 2
    #    if gamestate.tasks[0].completed_chimera is None and gamestate.tasks[0].completion < gamestate.tasks[0].progress:
    #        gamestate.tasks[0].completed_chimera = self
    #    return True

class leaderChimera(Chimera):
    def __init__(self, name):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('bb', 0, 1), Healer()], [Task(20, 0)])
        >>> gs.leader
        >>> gs = GameState([Chimera('bb', 0, 1), Healer()], [Task(20, 0)], leaderChimera('aa'))
        >>> gs.leader.name
        'aa'
        """
        self.name = name    

class ProfessionalManager(leaderChimera):
    def __init__(self, name='职业经理'):
        super().__init__(name)

    def debut(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('bb', 0, 1), Healer()], [Task(20, 0)], ProfessionalManager())
        >>> gs.place[0].chimera.energy
        4
        >>> gs.place[0].chimera.efficiency
        3
        >>> gs.place[1].chimera.efficiency
        5
        >>> gs.place[1].chimera.energy
        8
        """
        for place in gamestate.place:
            place.chimera.energy += 3
            place.chimera.efficiency += 3

class RuthlessDemon(leaderChimera):
    def __init__(self, name="严酷恶魔"):
        super().__init__(name)

    def settlement_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6)], [Task(1, 1)], RuthlessDemon())
        >>> gs.leader.name
        '严酷恶魔'
        >>> gs.place[0].chimera.efficiency
        6
        >>> gs.update()
        >>> gs.place[0].chimera.efficiency
        11
        """
        gamestate.tasks[0].completed_chimera.efficiency += 5

class CareerStandout(leaderChimera):
    def __init__(self, name="职场清流"):
        super().__init__(name)

    def debut(self, gamestate):
        for place in gamestate.place:
            place.chimera.efficiency += 2

    def praise(self, praised, gamestate):
        praised.efficiency += 2