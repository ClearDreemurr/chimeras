from place import *
from chimera import Onlooker, Bucktaker, KindPraiser, CareerStandout

class GameState:
    def __init__(self, chimeras, tasks, leader=None):
        self.len_chimeras = len(chimeras)
        self.tasks = tasks
        self.turns = 0
        self.chimera_place = {}
        self.place = self.make_place(chimeras)
        self.leader = leader
        self.debut()

    def input_praiser(self):
        self.praiser.extend([p.chimera for p in self.place if isinstance(p.chimera, KindPraiser)])
        if isinstance(self.leader, CareerStandout):
            self.praiser.append(self.leader)

    def debut(self):
        if self.leader:
            self.leader.debut(self)
        for p in self.place:
            if p.chimera:
                p.chimera.debut(self)

    
    def update(self):
        self.reparation_phase()
        self.work_phase()
        self.additional_phase()
        self.settlement_phase()

    def reparation_phase(self):
        for place in self.place:
            if place.chimera:
                place.chimera.action(self, 'prepare')
    
    def work_phase(self):
        self.place[0].chimera.action(self, 'work')

    def additional_phase(self):
        if "ShockForce" in self.chimera_place:
            self.rush(self.chimera_place["ShockForce"].chimera)
        if "Disservicer" in self.chimera_place:
            self.helpwork(self.chimera_place["Disservicer"].chimera)
        if "Creditstealer" in self.chimera_place:
            self.stealwork(self.chimera_place["Creditstealer"].chimera)
        if "Workaholic" in self.chimera_place:
            self.holicwork(self.chimera_place["Workaholic"].chimera)

    def rush(self, chimera):
        chimera.additional_action(self)

    def helpwork(self, chimera):    
        chimera.additional_action(self)
        if "Workaholic" in self.chimera_place:
            self.holicwork(self.chimera_place["Workaholic"].chimera)
        if "ShockForce" in self.chimera_place:
            self.rush(self.chimera_place["ShockForce"].chimera)
        self.praise(chimera)

    def stealwork(self, chimera):
        chimera.additional_action(self)
        if "Workaholic" in self.chimera_place:
            self.holicwork(self.chimera_place["Workaholic"].chimera)
        if "ShockForce" in self.chimera_place:
            self.rush(self.chimera_place["ShockForce"].chimera)
        self.praise(chimera)

    def holicwork(self, chimera):
        chimera.additional_action(self)
        if "ShockForce" in self.chimera_place:
            self.rush(self.chimera_place["ShockForce"].chimera)
        self.praise(chimera)

    def praise(self, chimera):
        if "KindPraiser" in self.chimera_place:
            self.chimera_place["KindPraiser"].chimera.praise(chimera, self)
        if isinstance(self.leader, CareerStandout):
            self.leader.praise(chimera, self)

    def settlement_phase(self):
        for place in self.place:
            if place.chimera:
                place.chimera.action(self, 'settle')
        if self.leader:
            self.leader.settlement_action(self)
        if self.tasks[0].is_completed():
            self.tasks = self.tasks[1:]
        for place in self.place:
            if place.chimera and place.chimera.energy<=0:
                for p in self.place:
                    if isinstance(p.chimera, Bucktaker):
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
        >>> gs = GameState([Chimera("aa", 10, 100), NormalChimera(), Workaholic()], [Task()])
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
        >>> gs.chimera_place["Chimera"] is gs.place[0]
        True
        >>> gs.chimera_place["NormalChimera"] is gs.place[1]
        True
        >>> "Workaholic" in gs.chimera_place
        True
        """
        places = []
        place0 = None
        for i in range(len(chimeras)):
            place1 = place(f"place{i}", chimeras[i], place0)
            chimeras[i].place = place1
            places.append(place1)
            self.chimera_place[chimeras[i].__class__.__name__] = place1
            place0 = place1
        return places

    def dead_skills(self):
        for place in self.place:
            if isinstance(place.chimera, Onlooker):
                place.chimera.skill()
            if isinstance(place.chimera, Bucktaker):
                place.next.exit(self)

            
    def swap(self, chimera0, next):
        """
        placeA      placeB  ->  placeA  placeB
        chimera0    next    ->  next    chimera0 #change place.chimera AND chimera.place
        """
        place1, place2 = chimera0.place, next.place
        place1.chimera, place2.chimera = next, chimera0
        place1.chimera.place = place1
        place2.chimera.place = place2
        self.chimera_place[chimera0.__class__.__name__], self.chimera_place[next.__class__.__name__] = chimera0.place, next.place
