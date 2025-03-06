from gamestate import *
from task import *
from chimera import *

def main():
    gs = GameState([Chimera('aa', 6, 6)], [Task(1, 1)], RuthlessDemon())
    while not gs.end():
        gs.update()

main()