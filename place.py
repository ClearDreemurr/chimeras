class place:
    def __init__(self, name, chimera, last=None):
        self.name = name
        self.chimera = chimera
        self.last = last
        self.next = None
        if last:
            last.next = self

    def add_chimera(self, chimera):
        self.chimera = chimera

    def remove_chimera(self):
        """
        >>> from chimera import *
        >>> from gamestate import *
        >>> from task import*
        >>> gs = GameState([Chimera("aa", 1, 1), Chimera("bb", 1, 1), Chimera("cc", 5, 10)], [Task(20, 1)])
        >>> [gs.place[i].chimera.name for i in range(gs.len_chimeras)]
        ['aa', 'bb', 'cc']
        >>> gs.place[0].next.chimera.name
        'bb'
        >>> gs.place[1].remove_chimera()
        >>> [gs.place[i].chimera.name for i in range(gs.len_chimeras-1)]
        ['aa', 'cc']
        >>> gs.place[0].next.chimera.name
        'cc'
        >>> gs.place[1].chimera.place is gs.place[1] #IMPORTANT!!!!!!!!!!!!!!!!!!
        True
        """
        self.chimera = None
        plc = self
        while plc.next and plc.next.chimera:
            plc.chimera = plc.next.chimera
            plc.chimera.place = plc
            plc = plc.next
        plc.chimera = None