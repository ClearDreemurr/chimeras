from gamestate import *
from task import *
from chimera import *

def main():
    gs = GameState([Chimera('aa', 6, 6), Disservicer(), KindPraiser(), Workaholic(), Creditstealer()], [Task(20, 5)])
    while not gs.end():
        gs.update()

main()