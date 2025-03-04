from chimera import *
from task import *
from gamestate import *

def main():
    chimeras = [NormalChimera(), Chimera("内卷王", 8, 5), NormalChimera()]

    tasks = [Task(), Task(), Task()]

    gamestate = GameState(chimeras, tasks)

    while not gamestate.end():
        gamestate.update()

    if gamestate.complete():
        print("\n任务完成！")
    else:
        print("\n任务未完成且所有奇美拉已退场，游戏结束！")

main()