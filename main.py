from gamestate import *
from task import *
from chimera import *

def main():
    chimeras = init_chimera_dict() #所有的奇美拉,用字典表示，其中key是每只奇美拉的名字，value是对应的奇美拉对象
    leaders = init_leader_dict()
    turn = 1 #从第一轮开始
    tasks = Task.turn_task(turn) #Task.turn_task(turn)返回第turn轮需要干的所有工作
    while turn <= 12: #工作一拱持续12轮
        selected_team, leader= show_selection_gui(chimeras) #得到用户选择的奇美拉和领队
        gs = GameState(selected_team, tasks, leaders) #本轮回合由selected_team 进行第turn轮工作
        while not gs.end(): #进行该轮工作直到该轮结束
            gs.update() #进行一次工作
        back(chimeras, gs.chimeras) #将gamestate中剩余的奇美拉归队，保留他们的状态，如果某只奇美拉的is_resting()返回True的则显示精力耗尽并不可选
        if gs.complete(): #如果工作完成了
            turn += 1 #回合数加一，进入下一轮
        else: #工作没完成，选择剩余的奇美拉继续工作
            if not chimeras: #全部奇美拉均耗尽精力退场
                show_lose_gui() #显示游戏失败的gui
                return #停止while
            else:
                tasks = gs.tasks #上次没做完的工作,紧接着下轮循环的前两行表示从剩余的奇美拉重新选择，以及由重新选择的奇美拉和上次没做完的工作构成新的gamestate继续工作

def show_selection_gui(): 
    #假设用户选择的是这些奇美拉
    return [{"Disservicer": Disservicer()}, {"KindPraiser":KindPraiser()}, {"Workaholic":Workaholic()}, {"Creditstealer":Creditstealer()}]

def init_chimera_dict():
    """
    >>> a = init_chimera_dict()
    >>> len(a)
    23
    """
    chimeras = {}
    chimeras["RatRaceKing"] = RatRaceKing()
    chimeras["BadTempered"] = BadTempered()
    chimeras["ToughCookie"] = ToughCookie()
    chimeras["AbsenteeFreak"] = AbsenteeFreak()
    chimeras["AbsenteeMaster"] = AbsenteeMaster()
    chimeras["Onlooker"] = Onlooker()
    chimeras["Healer"] = Healer()
    chimeras["Bucktaker"] = Bucktaker()
    chimeras["SmallGroup"] = SmallGroup()
    chimeras["EmptyPromises"] = EmptyPromises()
    chimeras["Creditstealer"] = Creditstealer()
    chimeras["Disservicer"] = Disservicer()
    chimeras["KindPraiser"] = KindPraiser()
    chimeras["Workaholic"] = Workaholic()
    chimeras["ShockForce"] = ShockForce()
    chimeras["WorkDitcher"] = WorkDitcher()
    chimeras["Complainer"] = Complainer()
    chimeras["Suffermaxxer"] = Suffermaxxer()
    chimeras["Uber_Negative"] = Uber_Negative()
    chimeras["OldHonest"] = OldHonest()
    chimeras["PressureMonster"] = PressureMonster()
    chimeras["LittleVillain"] = LittleVillain()
    chimeras["Slacker"] = Slacker()
    return chimeras

def init_leader_dict():
    leader = {}
    leader["ProfessionalManager"] = ProfessionalManager()
    leader["RuthlessDemon"] = RuthlessDemon()
    leader["CareerStandout"] = CareerStandout()
    return leader

def back(chimeras, back):
    for chimera in back:
        chimeras[chimera.__class__.__name__] = chimera

def show_lose_gui():
    pass


main()