from event_manager import publish

class Chimera:
    normal = False
    skill_text = None
    is_selectable = True
    def __init__(self, name, efficiency, energy):
        self.name = name
        self.efficiency = efficiency
        self.energy = energy
        self.place = None
        self.dialogs = "good job"

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
        #publish("chimera_skill_triggered", chimera=self, skill_text=self.skill)
        gamestate.tasks[0].do_progress(self.efficiency, gamestate)
        self.reduce_energy(gamestate.tasks[0].consumption, gamestate)
        if gamestate.tasks[0].is_completed():
            gamestate.tasks[0].completed_chimera = self

    def additional_action(self, gamestate):
        pass 

    def settlement_action(self, gamestate):
        pass

    def skill(self, gamestate):
        pass

    def is_alive(self):
        return self.energy > 0
    
    def reduce_energy(self, amount, gamestate):
        self.energy -= amount
        publish("attribute_change", obj=self, amount=-amount, gamestate=gamestate, attribute="energy")

    def increase_energy(self, amount, gamestate):
        self.energy += amount
        publish("attribute_change", obj=self, amount=amount, gamestate=gamestate, attribute="energy")

    def reduce_efficiency(self, amount, gamestate):
        self.efficiency -= amount
        publish("attribute_change", obj=self, amount=-amount, gamestate=gamestate, attribute="efficiency")

    def increase_efficiency(self, amount, gamestate):
        self.efficiency += amount
        publish("attribute_change", obj=self, amount=amount, gamestate=gamestate, attribute="efficiency")

    def debut(self, gamestate):#why????
        pass

    def is_resting(self):
        return self.energy <= 0
    
class NormalChimera(Chimera):
    normal = True
    skill_text = ""
    def __init__(self, name, efficiency, energy):
        super().__init__(name, efficiency, energy)

class Uber_Negative(NormalChimera):
    def __init__(self, name="负能量", efficiency=7, energy=2):
        super().__init__(name, efficiency, energy)

class OldHonest(NormalChimera):
    def __init__(self, name="真老实", efficiency=1, energy=16):
        super().__init__(name, efficiency, energy)

class PressureMonster(NormalChimera):
    def __init__(self, name="压力怪", efficiency=5, energy=3):
        super().__init__(name, efficiency, energy)

class LittleVillain(NormalChimera):
    def __init__(self, name="小坏蛋", efficiency=3, energy=5):
        super().__init__(name, efficiency, energy)

class Slacker(NormalChimera):
    def __init__(self, name="摸鱼仔", efficiency=3, energy=2):
        super().__init__(name, efficiency, energy)

class RatRaceKing(Chimera):
    skill_text = "完成工作时，+3精力，+2效率"
    def __init__(self, name="内卷王", efficiency=3, energy=8):
        super().__init__(name, efficiency, energy)

    def settlement_action(self, gamestate):
        if gamestate.tasks[0].completed_chimera is self:
            super().increase_energy(3, gamestate)
            super().increase_efficiency(2, gamestate)

class BadTempered(Chimera):
    skill_text = "损失精力时使下一只奇美拉-1精力"
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
    skill_text = "损失精力时使前后两只奇美拉+1效率"

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
        if self.place.next and self.place.next.chimera:
            self.place.next.chimera.increase_efficiency(1, gamestate)
        if self.place.last and self.place.last.chimera:
            self.place.last.chimera.increase_efficiency(1, gamestate)

class AbsenteeFreak(Chimera):
    skill_text = "损失精力时与后一只奇美拉交换位置并+2效率"
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
        >>> gs.chimera_place["AbsenteeFreak"] is gs.place[2]
        True
        """
        super().reduce_energy(amount, gamestate)
        if self.place.next.chimera:
            super().increase_efficiency(2, gamestate)
            gamestate.swap(self, self.place.next.chimera)

class AbsenteeMaster(Chimera):
    skill_text = "损失精力时与后一只奇美拉交换位置并+3精力"
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
            self.increase_energy(3, gamestate)
            gamestate.swap(self, self.place.next.chimera)

class Onlooker(Chimera):
    skill_text = "有奇美拉累倒时+2精力，+2效率"
    def __init__(self, name='看乐子', efficiency=3, energy=3):
        super().__init__(name, efficiency, energy)
    
    def skill(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 0, 1), Slacker(), Onlooker()], [Task(20, 5)])
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
        self.increase_energy(2, gamestate)
        self.increase_efficiency(2, gamestate)

class Healer(Chimera):
    skill_text = "回合开始时使前一只奇美拉+1精力"
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
        self.place.last.chimera.increase_energy(1, gamestate)

class Bucktaker(Chimera):
    skill_text = "有奇美拉累倒时使其+10精力，自身逃离工作"
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
        >>> len(gs.chimeras)
        2
        """
        return

class SmallGroup(Chimera):
    skill_text = "回合开始时使前面两只奇美拉+1效率，其余奇美拉-1精力"
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
            if place in up and place.chimera:
                place.chimera.increase_efficiency(1, gamestate)
            elif place is not self.place and place.chimera:
                place.chimera.reduce_energy(1, gamestate)

class EmptyPromises(Chimera):
    skill_text = "登场时使所有奇美拉+8效率，回合开始时，若它在场则所有奇美拉-2效率"
    def __init__(self, name="画饼王", efficiency=2, energy=7):
        super().__init__(name, efficiency, energy)

    def debut(self, gamestate):
        for place in gamestate.place:
            if place is not self.place and place.chimera:
                place.chimera.increase_efficiency(8, gamestate)
    
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
                place.chimera.reduce_efficiency(2, gamestate)

class WorkDitcher(Chimera):
    skill_text = "累倒时带着后一只奇美拉一起逃离工作并使所有奇美拉+8精力"
    def __init__(self, name="跑路侠", efficiency=1, energy=1):
        super().__init__(name, efficiency, energy)
    
    def skill(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([WorkDitcher(), Chimera('dd', 2, 2)], [Task(20, 5)])
        >>> gs.update()
        >>> len(gs.chimera_place)
        0
        >>> gs.chimeras[1].is_alive()
        True
        """
        self.place.next.remove_chimera(gamestate)
        for p in gamestate.place:
            if p.chimera:
                p.chimera.increase_energy(8, gamestate)
    
class Creditstealer(Chimera):
    skill_text = "同伴工作时，若自身效率>=剩余工作进度，则进行追加工作完成该工作"
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
            gamestate.tasks[0].do_progress(self.efficiency, gamestate)
            if gamestate.tasks[0].completed_chimera is None:
                gamestate.tasks[0].completed_chimera = self

class Disservicer(Chimera):
    skill_text = "同伴工作时发动一次追加工作"
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
        gamestate.tasks[0].do_progress(self.efficiency, gamestate)
        if gamestate.tasks[0].completed_chimera is None and gamestate.tasks[0].completion < gamestate.tasks[0].progress:
            gamestate.tasks[0].completed_chimera = self

class KindPraiser(Chimera):
    skill_text = "同伴进行追加工作时，使其+2效率"
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
            praised.increase_efficiency(2, gamestate)
    
class Workaholic(Chimera):
    skill_text = "同伴进行工作或追加工作时，进行一次自身50%效率的追加工作"
    def __init__(self, name="工作狂", efficiency=6, energy=10):
        super().__init__(name, efficiency, energy)

    def additional_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(20, 5)])
        >>> tmp = gs.tasks[0]
        >>> gs.update()
        >>> gs.place[1].chimera.efficiency
        -1
        >>> gs.place[3].chimera.efficiency
        12
        >>> tmp.completed_chimera is gs.place[4].chimera
        True
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(7, 5)])
        >>> tmp = gs.tasks[0]
        >>> gs.update()
        >>> gs.place[1].chimera.efficiency
        -1
        >>> gs.place[3].chimera.efficiency
        12
        >>> tmp.completed_chimera is gs.place[3].chimera
        True
        """
        gamestate.tasks[0].do_progress(self.efficiency / 2, gamestate)
        if gamestate.tasks[0].completed_chimera is None and gamestate.tasks[0].completion < gamestate.tasks[0].progress:
            gamestate.tasks[0].completed_chimera = self

class ShockForce(Chimera):
    skill_text = "同伴发动工作或追加工作时，与前一只奇美拉交换位置并+6精力"
    def __init__(self, name="急先锋", efficiency=2, energy=5):
        super().__init__(name, efficiency, energy)

    def additional_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), ShockForce()], [Task(20, 5)])
        >>> gs.update()
        >>> [p.chimera.name for p in gs.place]
        ['急先锋', 'aa', '帮倒忙']
        >>> gs.place[0].chimera.energy
        17
        >>> gs.chimera_place["ShockForce"] is gs.place[0]
        True
        >>> gs.chimera_place["Disservicer"] is gs.place[2]
        True
        >>> gs.chimera_place["Chimera"] is gs.place[1]
        True
        """
        if self.place.last.chimera:
            self.increase_energy(6, gamestate)
            gamestate.swap(self.place.last.chimera, self)

class MasterOrdinaire(Chimera):
    skill_text = "登场时，获得场上所有无特性同伴100%的精力和效率（单次上限25）"
    def __init__(self, name="平凡王", efficiency=7, energy=7):
        super().__init__(name, efficiency, energy)

    def debut(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), OldHonest(), MasterOrdinaire(), OldHonest(), Onlooker()], [Task(20, 5)])
        >>> gs.place[0].chimera.normal
        False
        >>> gs.place[1].chimera.normal
        True
        >>> gs.place[2].chimera.efficiency == gs.place[1].chimera.efficiency + 7 + gs.place[3].chimera.efficiency
        True
        >>> gs.place[2].chimera.energy == gs.place[1].chimera.energy + 7 + gs.place[3].chimera.energy
        True
        """
        total_energy = 0
        total_efficiency = 0
        for p in gamestate.place:
            if p.chimera.normal:
                total_energy += min(25, p.chimera.energy)
                total_efficiency += min(25, p.chimera.efficiency)
        self.increase_energy(total_energy, gamestate)
        self.increase_efficiency(total_efficiency, gamestate)

class Complainer(Chimera):
    skill_text = "使完成工作的同伴+4效率"
    def __init__(self, name="说怪话", efficiency=14, energy=1):
        super().__init__(name, efficiency, energy)

    def settlement_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 18), Complainer()], [Task(8, 1)], RuthlessDemon())
        >>> tmp = gs.tasks[0]
        >>> gs.place[0].chimera.efficiency
        6
        >>> gs.update()
        >>> gs.place[0].chimera.efficiency
        6
        >>> tmp.is_completed()
        False
        >>> gs.update()
        >>> gs.place[0].chimera.efficiency
        15
        >>> tmp.is_completed()
        True
        """
        if gamestate.tasks[0].is_completed():
            gamestate.tasks[0].completed_chimera.increase_efficiency(4,gamestate)

class Suffermaxxer(Chimera):
    skill_text = "损失精力时所有同伴+1效率"
    def __init__(self, name="受气包", efficiency=2, energy=5):
        super().__init__(name, efficiency, energy)

    def reduce_energy(self, amount, gamestate):
        """
        >>> from task import *
        >>> from gamestate import *
        >>> gs = GameState([BadTempered(), Suffermaxxer(), Chimera("aa", 5, 10), Chimera("bb", 10, 1), Onlooker()], [Task(20, 1)])
        >>> [p.chimera.efficiency for p in gs.place]
        [2, 2, 5, 10, 3]
        >>> gs.update()
        >>> [p.chimera.efficiency for p in gs.place]
        [3, 2, 6, 11, 4]
        """
        super().reduce_energy(amount, gamestate)
        for place in gamestate.place:
            if place.chimera is not self:
                place.chimera.increase_efficiency(1, gamestate)

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
    skill_text = "登场时全体奇美拉+3精力，+3效率"
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
            place.chimera.increase_energy(3, gamestate)
            place.chimera.increase_efficiency (3, gamestate)

class RuthlessDemon(leaderChimera):
    skill_text = "完成工作的奇美拉+4效率"
    def __init__(self, name="严酷恶魔"):
        super().__init__(name)

    def settlement_action(self, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 18)], [Task(8, 1)], RuthlessDemon())
        >>> tmp = gs.tasks[0]
        >>> gs.leader.name
        '严酷恶魔'
        >>> gs.place[0].chimera.efficiency
        6
        >>> gs.update()
        >>> gs.place[0].chimera.efficiency
        6
        >>> tmp.is_completed()
        False
        >>> gs.update()
        >>> gs.place[0].chimera.efficiency
        11
        >>> tmp.is_completed()
        True
        """
        if gamestate.tasks[0].is_completed():
            gamestate.tasks[0].completed_chimera.increase_efficiency(5, gamestate)

class CareerStandout(leaderChimera):
    skill_text = "登场时全体奇美拉+2效率，奇美拉进行追加工作时使其+1效率"
    def __init__(self, name="职场清流"):
        super().__init__(name)

    def debut(self, gamestate):
        for place in gamestate.place:
            place.chimera.increase_efficiency(2, gamestate)

    def praise(self, praised, gamestate):
        """
        >>> from gamestate import *
        >>> from task import *
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(25, 5)], CareerStandout())
        >>> tmp = gs.tasks[0]
        >>> gs.update()
        >>> gs.place[1].chimera.efficiency
        2
        >>> gs.place[3].chimera.efficiency
        17
        >>> tmp.completed_chimera is gs.place[4].chimera
        True
        >>> gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(10, 5)], CareerStandout())
        >>> tmp = gs.tasks[0]
        >>> gs.update()
        >>> gs.place[1].chimera.efficiency
        2
        >>> gs.place[3].chimera.efficiency
        17
        >>> tmp.completed_chimera is gs.place[3].chimera
        True
        """
        praised.increase_efficiency(1, gamestate)