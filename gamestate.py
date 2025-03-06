from place import *
from chimera import Onlooker, name2

class GameState:
    def __init__(self, chimeras, tasks, leader=None):
        self.len_chimeras = len(chimeras)
        self.tasks = tasks
        self.turns = 0
        self.place = self.make_place(chimeras)
        self.leader = leader
        if leader:
            leader.debut(self)

    
    def update(self):
        self.reparation_phase()
        self.work_phase()
        self.settlement_phase()

    def reparation_phase(self):
        for place in self.place:
            if place.chimera:
                place.chimera.action(self, 'prepare')
    
    def work_phase(self):
        self.place[0].chimera.action(self, 'work')

    def settlement_phase(self):
        for place in self.place:
            if place.chimera:
                place.chimera.action(self, 'settle')
        if self.tasks[0].is_completed():
            self.tasks = self.tasks[1:]
        for place in self.place:
            if place.chimera and place.chimera.energy<=0:
                for p in self.place:
                    if isinstance(p.chimera, name2):
                        p.remove_chimera(self)
                        place.chimera.energy += 10
                        return
                place.remove_chimera(self)
                return
                


    def end(self):
        return self.len_chimeras == 0 or not self.tasks
    
    def complete(self):
        return not self.tasks

    def make_place(self, chimeras):
        """
        >>> from chimera import *
        >>> from task import *
        >>> gs = GameState([Chimera("aa", 10, 100), NormalChimera(), NormalChimera()], [Task()])
        >>> gs.place[0].name
        'place0'
        >>> gs.place[0].chimera.name
        'aa'
        >>> gs.place[0].next.name
        'place1'
        >>> gs.place[0].last
        >>> gs.place[1].last is gs.place[0]
        True
        >>> gs.place[0].chimera.place is gs.place[0]
        True
        """
        places = []
        place0 = None
        for i in range(len(chimeras)):
            place1 = place(f"place{i}", chimeras[i], place0)
            chimeras[i].place = place1
            places.append(place1)
            place0 = place1
        return places

    def dead_skills(self):
        for place in self.place:
            if isinstance(place.chimera, Onlooker):
                place.chimera.skill()

            
    def swap(self, chimera0, next):
        """
        placeA      placeB  ->  placeA  placeB
        chimera0    next    ->  next    chimera0 #change place.chimera AND chimera.place
        """
        place1, place2 = chimera0.place, next.place
        place1.chimera, place2.chimera = next, chimera0
        place1.chimera.place = place1
        place2.chimera.place = place2