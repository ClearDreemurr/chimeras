from chimera import *
from task import *
from gamestate import *

def main():
    chimeras = [unnamed(), unnamed1()]
    turn_tasks = Task()
    tasks = turn_tasks.turn_task(1)

    gamestate = GameState(chimeras, tasks)

    while not gamestate.end():
        gamestate.update()

    if gamestate.complete():
        print("\n任务完成！")
    else:
        print("\n任务未完成且所有奇美拉已退场，游戏结束！")

main()