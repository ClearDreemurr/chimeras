from gamestate import *
from task import *
from chimera import *

def main():
    chimeras = [AbsenteeFreak(), AbsenteeMaster(), BadTempered(), ToughCookie(), Onlooker()]
    tasks = Task().turn_task(1)
    for chimera in chimeras:
        chimera.efficiency += 2
    gs = GameState(chimeras, tasks)

    while not gs.end():
        gs.update()

main()