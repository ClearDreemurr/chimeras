from gamestate import *
from task import *
from chimera import *

def main():
    gs = GameState([Chimera('aa', 0, 1), Chimera('bb', 0, 1), unnamed6()], [Task(20, 1)])
    print(gs.place[2].chimera.name)
    gs.update()
    print(gs.place[1].chimera.name)
    print(gs.place[1].chimera.efficiency)
    gs.update()
    print(gs.place[0].chimera.name)
    print(gs.place[0].chimera.efficiency)


main()