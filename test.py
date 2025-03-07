from chimera import *
from task import *
from gamestate import *

def main():
    gs = GameState([WorkDitcher(), Chimera('dd', 2, 2)], [Task(20, 5)])

    while not gs.end():
        gs.update()

    if gs.complete():
        print("\n任务完成！")
    else:
        print("\n任务未完成且所有奇美拉已退场，游戏结束！")

main()