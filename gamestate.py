class GameState:
    def __init__(self, chimeras, tasks):
        self.chimeras = chimeras
        self.tasks = tasks
        self.turns = 0
    
    def update(self):
        self.reparation_phase()
        self.work_phase()
        self.settlement_phase()

    def reparation_phase(self):
        for chimera in self.chimeras:
            chimera.action(self, 'prepare')
    
    def work_phase(self):
        self.chimeras[0].action(self, 'work')

    def settlement_phase(self):
        for chimera in self.chimeras:
            chimera.action(self, 'settle')
        if self.tasks[0].is_completed():
            self.tasks = self.tasks[1:]
        self.chimeras = [chimera for chimera in self.chimeras if chimera.is_alive()]

    def end(self):
        return not self.chimeras or not self.tasks
    
    def complete(self):
        return not self.tasks