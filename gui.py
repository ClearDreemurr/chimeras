# gui.py
import pygame
import sys
from chimera import *  # 假设这些类定义在 chimera 模块中
from task import Task                   # 任务类
from gamestate import GameState
from place import place
from event_manager import register

skill_box_expire_time = 0
current_skill_chimera = None

def main():
    chimeras = init_chimera_dict() #所有的奇美拉,用字典表示，其中key是每只奇美拉的名字，value是对应的奇美拉对象
    leaders = init_leader_dict()
    turn = 1 #从第一轮开始
    tasks = Task().turn_task(turn)
    while turn <= 12: #工作一拱持续12轮
        selected_team, leader= show_selection_gui(chimeras, leaders) #得到用户选择的奇美拉和领队
        gs = GameState(selected_team, tasks, leader) #本轮回合由selected_team 进行第turn轮工作
        gs = main_loop(gs)
        back(chimeras, gs.chimeras) #将gamestate中剩余的奇美拉归队，保留他们的状态，如果某只奇美拉的is_resting()返回True的则显示精力耗尽并不可选
        if gs.complete(): #如果工作完成了
            turn += 1 #回合数加一，进入下一轮
            tasks = Task().turn_task(turn) #Task.turn_task(turn)返回第turn轮需要干的所有工作
        else: #工作没完成，选择剩余的奇美拉继续工作
            if not chimeras: #全部奇美拉均耗尽精力退场
                show_lose_gui() #显示游戏失败的gui
                return #停止while
            else:
                tasks = gs.tasks #上次没做完的工作,紧接着下轮循环的前两行表示从剩余的奇美拉重新选择，以及由重新选择的奇美拉和上次没做完的工作构成新的gamestate继续工作

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
        if chimera.energy <= 0:
            chimera.is_selectable = False
        chimeras[chimera.__class__.__name__] = chimera
    # 将chimeras按 is_selectable 排序，把False排后
    sorted_list = sorted(chimeras.values(), key=lambda x: x.is_selectable, reverse=True)
    # 重新构造chimeras
    new_dict = {}
    for chim in sorted_list:
        new_dict[chim.name] = chim
    chimeras.clear()
    chimeras.update(new_dict)

def show_lose_gui():
    pass

# 尝试加载支持中文的字体，否则使用默认字体
pygame.font.init()
try:
    font = pygame.font.SysFont("SimHei", 20)
    big_font = pygame.font.SysFont("SimHei", 30)
except Exception:
    font = pygame.font.SysFont("Arial", 20)
    big_font = pygame.font.SysFont("Arial", 30)

# 初始化 Pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("奇美拉工作模拟")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
BLUE  = (100, 149, 237)
RED   = (220, 20, 60)
GREEN = (34, 139, 34)

# 定义区域：
# 左侧区域用于显示 place（奇美拉）队列
LEFT_AREA = pygame.Rect(120, 50, int(WIDTH * 0.65), HEIGHT - 150)
RIGHT_AREA = pygame.Rect(LEFT_AREA.right + 20, 50, WIDTH - LEFT_AREA.right - 70, HEIGHT - 150)
LEADER_DISPLAY_AREA = pygame.Rect(100, 200, 200, 150)
PROGRESS_AREA = pygame.Rect(WIDTH * 0.35, 10, WIDTH * 0.3, 20)

# 定义“下一回合”按钮区域
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_RECT = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT)

# 定义显示尺寸与间隔
PLACE_WIDTH = 160      # 每个 place 显示区域大小（用于显示其中奇美拉信息）
PLACE_HEIGHT = 100
PLACE_SPACING = 20

TASK_WIDTH = 200
TASK_HEIGHT = 200

# 动画移动速度（像素/帧）
MOVE_SPEED = 100

# --- GUI 层计算位置 ---
def compute_place_positions(place_list):
    """
    根据 place_list 中元素数量计算每个 place 在 LEFT_AREA 内的目标显示位置，
    排列顺序为从右到左，place_list[0] 显示在最右侧
    """
    positions = []
    for idx in range(len(place_list)):
        x = LEFT_AREA.right - (PLACE_WIDTH + PLACE_SPACING) * (idx + 1)
        y = LEFT_AREA.bottom - PLACE_HEIGHT - 100  # 距离底边 10 像素
        positions.append([x, y])
    return positions

def compute_task_position():
    """
    任务表格固定显示在 RIGHT_AREA 内居中
    """
    x = RIGHT_AREA.centerx - TASK_WIDTH // 2
    y = y = LEFT_AREA.bottom - PLACE_HEIGHT - 220  # 距离底边 10 像素

    return [x, y]


# 初始计算位置
task_position = compute_task_position()

def handle_attribute_change(obj, amount, gamestate, attribute):
    target_positions = compute_place_positions(gamestate.place)
    current_positions = [pos[:] for pos in target_positions]
    # 根据 obj 的类型判断是奇美拉还是任务，并获取它所在的显示区域
    # 例如：
    if hasattr(obj, "place") and obj.place is not None:
        # 找到奇美拉在 gamestate.place 中的索引，计算显示位置
        index = None
        for idx, p in enumerate(gamestate.place):
            if p == obj.place:
                index = idx
                break
        offset = -30 if attribute == 'energy' else 30
        if index is not None:
            pos = current_positions[index]
            display_pos = (pos[0] + PLACE_WIDTH // 2 - offset, pos[1] - 15)
        else:
            display_pos = (0, 0)
    else:
        display_pos = (task_position[0] + TASK_WIDTH // 2, task_position[1] - 15)
    
    # 绘制浮动数字并暂停1秒
    change_text, color = f"{amount}", GRAY
    if amount > 0:
        change_text, color = f"+{amount}", GREEN
    draw_floating_number(display_pos, change_text, color)

"""# 事件处理函数
def handle_chimera_skill_triggered(chimera, skill_text):
    # 计算技能文本框的区域
    rect = get_skill_text_rect(chimera)
    draw_skill_box(chimera, rect)  # 显示技能框

    hide_skill_box(rect)  # 隐藏技能框
"""
# 注册事件
register("attribute_change", handle_attribute_change)
#register("chimera_skill_triggered", handle_chimera_skill_triggered)

# 计算技能文本框的区域
"""def get_skill_text_rect(chimera):
    pos = get_chimera_screen_position(chimera)
    width, height = 200, 50  # 假设技能框宽度 200，高度 50
    rect = pygame.Rect(pos[0] - width // 2, pos[1] - height - 10, width, height)
    return rect
"""
# 计算奇美拉在屏幕上的位置
"""def get_chimera_screen_position(chimera):
    if hasattr(chimera, "place") and chimera.place is not None:
        index = None
        for idx, p in enumerate(gamestate.place):
            if p == chimera.place:
                index = idx
                break
        if index is not None:
            return (current_positions[index][0] + PLACE_WIDTH // 2, current_positions[index][1] - 15)
    return (0, 0)

def hide_skill_box(rect):
    # 这里可以用重绘背景区域的方法来清除技能框
    pygame.draw.rect(screen, (0, 0, 0), rect)  # 用背景色覆盖
    pygame.display.update()
"""
# --- 绘制函数 ---
def draw_places(screen, place_list, positions):
    """
    在屏幕上绘制每个 place 中奇美拉的信息。每个 place 绘制为一个表格，
    显示奇美拉的名称、工作效率（左下角）和精力（右下角）。
    如果 place.chimera 为 None，则显示“空”。
    """
    for idx, place_obj in enumerate(place_list):
        pos = positions[idx]
        rect = pygame.Rect(pos[0], pos[1], PLACE_WIDTH, PLACE_HEIGHT)
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        if place_obj.chimera:
            chimera = place_obj.chimera
            name_surf = font.render(str(chimera.name), True, BLACK)
            name_rect = name_surf.get_rect(center=(rect.centerx, rect.top + 15))
            screen.blit(name_surf, name_rect)
            eff_surf = font.render(f"效率:{chimera.efficiency}", True, BLUE)
            eff_rect = eff_surf.get_rect(bottomleft=(rect.left+5, rect.bottom-5))
            screen.blit(eff_surf, eff_rect)
            energy_surf = font.render(f"能量:{chimera.energy}", True, RED)
            energy_rect = energy_surf.get_rect(bottomright=(rect.right-5, rect.bottom-5))
            screen.blit(energy_surf, energy_rect)
        else:
            empty_surf = font.render("空", True, BLACK)
            empty_rect = empty_surf.get_rect(center=rect.center)
            screen.blit(empty_surf, empty_rect)

        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos) and place_obj.chimera:
            # 当悬停时绘制技能文本框
            draw_skill_box(place_obj.chimera, rect)

def draw_leader(leader):
    if leader:
        # 绘制背景（可选：用填充色）
        pygame.draw.rect(screen, GRAY, LEADER_DISPLAY_AREA)
        # 绘制边框（如果你不希望边框，则删除这一行）
        pygame.draw.rect(screen, BLACK, LEADER_DISPLAY_AREA, 2) 
        # 绘制领队名字，居中显示在框内偏上
        name_surf = big_font.render(leader.name, True, BLACK)
        name_rect = name_surf.get_rect(center=(LEADER_DISPLAY_AREA.centerx, LEADER_DISPLAY_AREA.y + 20))
        screen.blit(name_surf, name_rect)


def draw_task(screen, task, pos):
    rect = pygame.Rect(pos[0], pos[1], TASK_WIDTH, TASK_HEIGHT)
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    title_surf = font.render("工作", True, BLACK)
    title_rect = title_surf.get_rect(center=(rect.centerx, rect.top+15))
    screen.blit(title_surf, title_rect)
    # 新增工作进度条
    bar_width = TASK_WIDTH - 80
    bar_height = 20  # 较小的高度
    bar_x = rect.x + 70
    bar_y = rect.y + 175  # 稍微偏上一点的位置
    # 背景条
    pygame.draw.rect(screen, (220,220,220), (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * (task.progress / task.completion))
    pygame.draw.rect(screen, (0,200,0), (bar_x, bar_y, fill_width, bar_height))

    cons_surf = font.render(f"消耗:{task.consumption}", True, BLUE)
    cons_rect = cons_surf.get_rect(bottomleft=(rect.left+5, rect.bottom-5))
    screen.blit(cons_surf, cons_rect)
    prog_surf = font.render(f"{task.progress}/{task.completion}", True, RED)
    prog_rect = prog_surf.get_rect(bottomright=(rect.right-50, rect.bottom-5))
    screen.blit(prog_surf, prog_rect)
    
def wrap_text_chinese(text, font, max_width):
    """
    按字符对中文文本进行自动换行。
    返回一个字符串列表，每个元素代表一行文本。
    """
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # 当前行已经到达最大宽度，换行
            lines.append(current_line)
            current_line = char
    # 把最后一行加入
    if current_line:
        lines.append(current_line)
    return lines

def render_colored_text(surface, text, font, x, y):
    """
    仅当 "精力" 或 "效率" 之前直接跟着 "+/-数字" 时，才变色
    - "+2精力" → 红色
    - "-3效率" → 蓝色
    其他情况保持白色
    """
    i = 0
    while i < len(text):
        if text[i] in "+-" and i + 1 < len(text) and text[i+1].isdigit():
            # 读取完整数值
            num = text[i]
            i += 1
            while i < len(text) and text[i].isdigit():
                num += text[i]
                i += 1

            # 仅当数值后面是 "精力" 或 "效率" 时才变色
            if i < len(text) - 1 and text[i:i+2] in ["精力", "效率"]:
                keyword = text[i:i+2]
                color = RED if keyword == "精力" else BLUE
                word = num + keyword  # 让数字在前
                i += 2
            else:
                color = WHITE
                word = num  # 只是普通数字，不变色
        else:
            color = WHITE
            word = text[i]
            i += 1

        text_surf = font.render(word, True, color)
        surface.blit(text_surf, (x, y))
        x += text_surf.get_width()

def draw_skill_box(chimera, rect):
    # 定义文本框宽度和高度，可以与 rect 相同或者稍宽
    global skill_box_expire_time, current_skill_chimera
    
    box_width = rect.width + 20
    box_height = 100
    box_x = rect.centerx - box_width // 2
    box_y = rect.top - box_height - 5  # 在上方 5 像素处
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    
    # 创建半透明表面
    s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    s.fill((50,50,50,180))  # 灰色半透明背景
    screen.blit(s, (box_x, box_y))
    
    # 使用按字符换行的函数
    lines = wrap_text_chinese(chimera.skill_text, font, box_width - 20)
    line_height = font.get_linesize()
    y_offset = box_y + 10
    for line in lines:
        render_colored_text(screen, line, font, box_x + 10, y_offset)
        y_offset += line_height
        if y_offset > (box_y + box_height - line_height):
            break

def draw_progress_bar(completed, total=5):
    x, y = PROGRESS_AREA.topleft
    bar_width = PROGRESS_AREA.width
    bar_height = PROGRESS_AREA.height
    # 绘制背景条（灰色）
    pygame.draw.rect(screen, (200,200,200), (x, y, bar_width, bar_height))
    # 计算填充宽度：completed/total 的比例
    fill_width = int(bar_width * (completed / total))
    # 绘制填充条（绿色）
    pygame.draw.rect(screen, (0,200,0), (x, y, fill_width, bar_height))
    # 显示文字，例如 "2/5"
    text = font.render(f"工作进度：{completed}/{total}", True, BLACK)
    text_rect = text.get_rect(center=PROGRESS_AREA.center)
    screen.blit(text, text_rect)


def draw_button(screen):
    pygame.draw.rect(screen, GREEN, BUTTON_RECT)
    btn_text = font.render("下一回合", True, BLACK)
    btn_rect = btn_text.get_rect(center=BUTTON_RECT.center)
    screen.blit(btn_text, btn_rect)

def draw_floating_number(display_pos, change_text, color):
    # 绘制浮动数字：构造显示文本，例如 "+2" 或 "-3"
    # 创建一个临时表面，使用大字体显示
    temp_surf = big_font.render(change_text, True, color)
    temp_rect = temp_surf.get_rect(center=display_pos)
    
    # 为实现显示一秒效果，可以先在屏幕上绘制后调用 pygame.time.delay(1000)
    # 保存当前屏幕，绘制数字，然后等待 1 秒，再恢复背景（这里较为简化）
    screen.blit(temp_surf, temp_rect)
    pygame.display.update()
    pygame.time.delay(1000)
    pygame.draw.rect(screen, WHITE, temp_rect)
    pygame.display.update(temp_rect)

def draw_game_over(screen):
    over_surf = big_font.render("游戏结束！", True, RED)
    over_rect = over_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(over_surf, over_rect)

# --- 动画更新函数 ---
def update_positions(current, target):
    """
    对 current 位置逐帧靠近 target 位置，每个坐标分量以 MOVE_SPEED 像素/帧移动，
    返回是否所有位置都已达到目标
    """
    all_done = True
    for pos, targ in zip(current, target):
        # x 坐标更新
        if abs(pos[0] - targ[0]) <= MOVE_SPEED:
            pos[0] = targ[0]
        elif pos[0] < targ[0]:
            pos[0] += MOVE_SPEED
            all_done = False
        elif pos[0] > targ[0]:
            pos[0] -= MOVE_SPEED
            all_done = False
        # y 坐标更新
        if abs(pos[1] - targ[1]) <= MOVE_SPEED:
            pos[1] = targ[1]
        elif pos[1] < targ[1]:
            pos[1] += MOVE_SPEED
            all_done = False
        elif pos[1] > targ[1]:
            pos[1] -= MOVE_SPEED
            all_done = False
    return all_done


def show_selection_gui(chimeras, leaders):
    LIST_ITEM_WIDTH = 220
    LIST_ITEM_HEIGHT = 60
    LIST_ITEM_SPACING = 10

    TEAM_SLOT_WIDTH = 80
    TEAM_SLOT_HEIGHT = 80
    TEAM_SLOT_SPACING = 10

    LEADER_BTN_RECT = pygame.Rect(WIDTH - 150, 20, 130, 40)   # “选择领队”按钮
    START_BTN_RECT  = pygame.Rect(WIDTH - 150, HEIGHT - 60, 130, 40)  # “开始工作”按钮

    # 翻页按钮区域
    PAGE_BTN_WIDTH = 40
    PAGE_BTN_HEIGHT = 40
    PREV_PAGE_RECT = pygame.Rect(20, HEIGHT - 70, PAGE_BTN_WIDTH, PAGE_BTN_HEIGHT)
    NEXT_PAGE_RECT = pygame.Rect(70, HEIGHT - 70, PAGE_BTN_WIDTH, PAGE_BTN_HEIGHT)

    # 领队选择弹窗区域
    LEADER_POPUP_RECT = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)
    CLOSE_BTN_RECT = pygame.Rect(LEADER_POPUP_RECT.right - 30, LEADER_POPUP_RECT.top, 30, 30)

    # 定义技能文本显示区域（位于画面中间右侧）
    SKILL_BOX_RECT = pygame.Rect(WIDTH - 350, HEIGHT//2 - 50, 300, 50)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("选择奇美拉组队")

    # 把 chimeras 转成列表方便翻页
    chimera_items = list(chimeras.items())  # [(name, chimera_obj), ...]
    page_size = 8  # 每页显示6个奇美拉
    current_page = 0

    selected_team = []  # 已选择的奇美拉对象列表
    selected_leader = None

    # 领队弹窗相关
    leader_popup = False  # 是否显示领队选择弹窗
    leader_list = list(leaders.items())  # [(name, leader_obj), ...]

    clock = pygame.time.Clock()
    
    def draw_chimera_list():
        """
        在左侧区域绘制当前页面的奇美拉列表
        """
        # 计算本页要显示的 chimeras
        start_idx = current_page * page_size
        end_idx = min(len(chimera_items), start_idx + page_size)
        visible_items = chimera_items[start_idx:end_idx]

        x = 20
        y = 20
        for i, (c_name, c_obj) in enumerate(visible_items):
            rect = pygame.Rect(x, y, LIST_ITEM_WIDTH, LIST_ITEM_HEIGHT)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            # 判断是否已在 selected_team 中
            color = RED if c_obj in selected_team else BLACK
            pygame.draw.rect(screen, color, rect, 2)

            # 显示奇美拉名字和属性
            text_surf = font.render(f"{c_obj.name}  eff:{c_obj.efficiency} ene:{c_obj.energy}", True, BLACK)
            screen.blit(text_surf, (rect.x + 5, rect.y + 5))
            y += LIST_ITEM_HEIGHT + LIST_ITEM_SPACING

    def draw_team_slots():
        """
        在右下角绘制5个槽位，显示已选奇美拉
        """
        base_x = WIDTH - 300
        base_y = HEIGHT - 150
        for i in range(5):
            slot_rect = pygame.Rect(base_x + i*(TEAM_SLOT_WIDTH + TEAM_SLOT_SPACING), base_y, TEAM_SLOT_WIDTH, TEAM_SLOT_HEIGHT)
            pygame.draw.rect(screen, GRAY, slot_rect)
            pygame.draw.rect(screen, BLACK, slot_rect, 2)
            if i < len(selected_team):
                chimera_obj = selected_team[i]
                name_surf = font.render(chimera_obj.name, True, BLACK)
                screen.blit(name_surf, (slot_rect.x+5, slot_rect.y+5))
                # 显示属性
                prop_surf = font.render(f"E:{chimera_obj.efficiency}, N:{chimera_obj.energy}", True, BLACK)
                screen.blit(prop_surf, (slot_rect.x+5, slot_rect.y+25))

    def draw_leader_button():
        """
        在右上角画一个按钮显示当前领队或“选择领队”
        """
        pygame.draw.rect(screen, GREEN, LEADER_BTN_RECT)
        if selected_leader:
            text_surf = font.render(f"领队:{selected_leader.name}", True, BLACK)
        else:
            text_surf = font.render("选择领队", True, BLACK)
        txt_rect = text_surf.get_rect(center=LEADER_BTN_RECT.center)
        screen.blit(text_surf, txt_rect)

    def draw_start_button():
        """
        如果 selected_team >=1，显示“开始工作”按钮
        """
        if len(selected_team) >= 1:
            pygame.draw.rect(screen, (0,200,0), START_BTN_RECT)
            text_surf = font.render("开始工作", True, BLACK)
            txt_rect = text_surf.get_rect(center=START_BTN_RECT.center)
            screen.blit(text_surf, txt_rect)

    def draw_paging_buttons():
        """
        翻页按钮
        """
        # prev
        pygame.draw.rect(screen, GRAY, PREV_PAGE_RECT)
        pygame.draw.rect(screen, BLACK, PREV_PAGE_RECT, 2)
        ptext = font.render("<", True, BLACK)
        ptext_rect = ptext.get_rect(center=PREV_PAGE_RECT.center)
        screen.blit(ptext, ptext_rect)
        # next
        pygame.draw.rect(screen, GRAY, NEXT_PAGE_RECT)
        pygame.draw.rect(screen, BLACK, NEXT_PAGE_RECT, 2)
        ntext = font.render(">", True, BLACK)
        ntext_rect = ntext.get_rect(center=NEXT_PAGE_RECT.center)
        screen.blit(ntext, ntext_rect)

    def draw_leader_popup():
        """
        领队选择弹窗
        """
        pygame.draw.rect(screen, (220,220,220), LEADER_POPUP_RECT)
        pygame.draw.rect(screen, BLACK, LEADER_POPUP_RECT, 2)
        # 关闭按钮
        close_rect = pygame.Rect(LEADER_POPUP_RECT.right - 30, LEADER_POPUP_RECT.top, 30, 30)
        pygame.draw.rect(screen, RED, close_rect)
        ctext = font.render("X", True, BLACK)
        screen.blit(ctext, (close_rect.x+10, close_rect.y+5))

        # 显示3个领队
        lx = LEADER_POPUP_RECT.x + 10
        ly = LEADER_POPUP_RECT.y + 40
        lw = LEADER_POPUP_RECT.width - 20
        lh = 60
        for i, (lname, lobj) in enumerate(leader_list):
            item_rect = pygame.Rect(lx, ly + i*(lh+10), lw, lh)
            pygame.draw.rect(screen, GRAY, item_rect)
            pygame.draw.rect(screen, BLACK, item_rect, 2)
            # 显示名字
            name_surf = font.render(lobj.name, True, BLACK)
            screen.blit(name_surf, (item_rect.x+5, item_rect.y+5))
            # 显示技能介绍
            skill_surf = font.render(f"技能:{lobj.skill_text}", True, BLACK)

            screen.blit(skill_surf, (item_rect.x+5, item_rect.y+30))

    def leader_popup_click(pos):
        """
        处理领队弹窗的点击事件
        """
        close_rect = pygame.Rect(LEADER_POPUP_RECT.right - 30, LEADER_POPUP_RECT.top, 30, 30)
        if close_rect.collidepoint(pos):
            return "close"
        # 检查点击3个领队
        lx = LEADER_POPUP_RECT.x + 10
        ly = LEADER_POPUP_RECT.y + 40
        lw = LEADER_POPUP_RECT.width - 20
        lh = 60
        for i, (lname, lobj) in enumerate(leader_list):
            item_rect = pygame.Rect(lx, ly + i*(lh+10), lw, lh)
            if item_rect.collidepoint(pos):
                return lobj  # 返回选中的领队对象
        return None
    
    def draw_chimera_list(screen, chimera_items, current_page, page_size, selected_team):
        x = 20
        y = 20
        start_idx = current_page * page_size
        end_idx = min(len(chimera_items), start_idx + page_size)
        visible_items = chimera_items[start_idx:end_idx]
        for i, (c_name, c_obj) in enumerate(visible_items):
            rect = pygame.Rect(x, y, LIST_ITEM_WIDTH, LIST_ITEM_HEIGHT)
            pygame.draw.rect(screen, GRAY, rect)
            # 如果已选则用红色边框，否则黑色
            color = RED if c_obj in selected_team else BLACK
            pygame.draw.rect(screen, color, rect, 2)
            text_surf = font.render(f"{c_obj.name}: 精力{c_obj.efficiency},效率{c_obj.energy}", True, BLACK)
            screen.blit(text_surf, (rect.x+5, rect.y+5))
            y += LIST_ITEM_HEIGHT + LIST_ITEM_SPACING

    def draw_paging_buttons(screen):
        pygame.draw.rect(screen, GRAY, PREV_PAGE_RECT)
        pygame.draw.rect(screen, BLACK, PREV_PAGE_RECT, 2)
        ptext = font.render("<", True, BLACK)
        screen.blit(ptext, ptext.get_rect(center=PREV_PAGE_RECT.center))
        
        pygame.draw.rect(screen, GRAY, NEXT_PAGE_RECT)
        pygame.draw.rect(screen, BLACK, NEXT_PAGE_RECT, 2)
        ntext = font.render(">", True, BLACK)
        screen.blit(ntext, ntext.get_rect(center=NEXT_PAGE_RECT.center))

    def draw_team_slots(screen, selected_team):
        base_x = WIDTH - 450
        base_y = HEIGHT - 120
        for i in range(5):
            slot_rect = pygame.Rect(base_x + i*(TEAM_SLOT_WIDTH + TEAM_SLOT_SPACING), base_y, TEAM_SLOT_WIDTH, TEAM_SLOT_HEIGHT)
            pygame.draw.rect(screen, GRAY, slot_rect)
            pygame.draw.rect(screen, BLACK, slot_rect, 2)
            if i < len(selected_team):
                chimera_obj = selected_team[i]
                name_surf = font.render(chimera_obj.name, True, BLACK)
                screen.blit(name_surf, (slot_rect.x+5, slot_rect.y+5))
                prop_surf = font.render(f"E:{chimera_obj.efficiency},N:{chimera_obj.energy}", True, BLACK)
                screen.blit(prop_surf, (slot_rect.x+5, slot_rect.y+25))

    def draw_leader_button(screen, selected_leader):
        pygame.draw.rect(screen, GREEN, LEADER_BTN_RECT)
        if selected_leader:
            text_surf = font.render(f"领队:{selected_leader.name}", True, BLACK)
        else:
            text_surf = font.render("选择领队", True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=LEADER_BTN_RECT.center))

    def draw_leader_popup(screen, leader_list, selected_leader):
        pygame.draw.rect(screen, (220,220,220), LEADER_POPUP_RECT)
        pygame.draw.rect(screen, BLACK, LEADER_POPUP_RECT, 2)
        close_rect = pygame.Rect(LEADER_POPUP_RECT.right - 30, LEADER_POPUP_RECT.top, 30, 30)
        pygame.draw.rect(screen, RED, close_rect)
        ctext = font.render("X", True, BLACK)
        screen.blit(ctext, (close_rect.x+10, close_rect.y+5))

        lx = LEADER_POPUP_RECT.x + 10
        ly = LEADER_POPUP_RECT.y + 40
        lw = LEADER_POPUP_RECT.width - 20
        lh = 70
        for i, (lname, lobj) in enumerate(leader_list):
            item_rect = pygame.Rect(lx, ly + i*(lh+10), lw, lh)
            pygame.draw.rect(screen, GRAY, item_rect)
            pygame.draw.rect(screen, BLACK, item_rect, 2)
            if lobj == selected_leader:
                pygame.draw.rect(screen, RED, item_rect, 3)
            # 显示名字
            name_surf = font.render(lname, True, BLACK)
            screen.blit(name_surf, (item_rect.x+5, item_rect.y+5))
            # 技能介绍(仅示例)
            skill_surf = font.render(f"技能: {lobj.__class__.__name__}", True, BLACK)
            screen.blit(skill_surf, (item_rect.x+5, item_rect.y+35))

    def draw_start_button(screen):
        pygame.draw.rect(screen, (0,200,0), START_BTN_RECT)
        text_surf = font.render("开始工作", True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=START_BTN_RECT.center))
        
    # 主循环
    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # 领队弹窗逻辑
                if leader_popup:
                    result = leader_popup_click((mx, my))
                    if result == "close":
                        leader_popup = False
                    elif result and isinstance(result, leaderChimera):
                        selected_leader = result
                        leader_popup = False
                else:
                    # 检查翻页按钮
                    if PREV_PAGE_RECT.collidepoint(mx, my):
                        if current_page > 0:
                            current_page -= 1
                    elif NEXT_PAGE_RECT.collidepoint(mx, my):
                        max_page = (len(chimera_items) - 1) // page_size
                        if current_page < max_page:
                            current_page += 1
                    # 检查点击左侧列表
                    else:
                        # 计算本页显示的 chimeras
                        start_idx = current_page * page_size
                        end_idx = min(len(chimera_items), start_idx + page_size)
                        visible_items = chimera_items[start_idx:end_idx]
                        x = 20
                        y = 20
                        for i, (c_name, c_obj) in enumerate(visible_items):
                            rect = pygame.Rect(x, y, LIST_ITEM_WIDTH, LIST_ITEM_HEIGHT)
                            if rect.collidepoint(mx, my):
                                # 如果该奇美拉已在 selected_team，则移除
                                if c_obj in selected_team:
                                    selected_team.remove(c_obj)
                                else:
                                    # 若未满5只，添加
                                    if len(selected_team) < 5:
                                        selected_team.append(c_obj)
                                mouse_pos = pygame.mouse.get_pos()
                                if SKILL_BOX_RECT.collidepoint(mouse_pos) and c_obj.chimera:
                                    # 当悬停时绘制技能文本框
                                    draw_skill_box(c_obj, SKILL_BOX_RECT)
                                break
                            y += LIST_ITEM_HEIGHT + LIST_ITEM_SPACING
                        
                        # 检查队伍区域点击：若点击队伍里某只奇美拉，再点击空白处则出队
                        # (可选逻辑，这里不写也行)
                        
                        # 检查领队按钮
                        if LEADER_BTN_RECT.collidepoint(mx, my):
                            leader_popup = True
                        # 检查开始工作按钮
                        if len(selected_team) >= 1 and START_BTN_RECT.collidepoint(mx, my):
                            # 返回 (selected_team, selected_leader)
                            return (selected_team, selected_leader)
        
        # 绘制可翻页奇美拉列表
        draw_chimera_list(screen, chimera_items, current_page, page_size, selected_team)
        # 绘制翻页按钮
        draw_paging_buttons(screen)
        # 绘制队伍槽位
        draw_team_slots(screen, selected_team)
        # 绘制领队按钮
        draw_leader_button(screen, selected_leader)
        # 若领队弹窗打开，绘制弹窗
        if leader_popup:
            draw_leader_popup(screen, leader_list, selected_leader)
        # 绘制开始工作按钮
        if len(selected_team) >= 1:
            draw_start_button(screen)

        pygame.display.update()
        clock.tick(60)

# --- 主循环 ---
def main_loop(gamestate):
    clock = pygame.time.Clock()
    running = True
    while running:
        target_positions = compute_place_positions(gamestate.place)
        current_positions = [pos[:] for pos in target_positions]

        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if BUTTON_RECT.collidepoint(mouse_pos):
                    print("点击了下一回合按钮")
                    gamestate.update()  # 更新一回合（包括准备、工作和结算阶段）
                    # 重新计算目标位置，注意 gamestate.place 为 place 列表
                    target_positions = compute_place_positions(gamestate.place)
                else:
                    # 其他点击处理（此处可添加奇美拉详情弹窗等功能）
                    pass
        # 更新当前显示位置向目标位置平滑移动
        update_positions(current_positions, target_positions)
        screen.fill(WHITE)
        pygame.draw.rect(screen, WHITE, LEFT_AREA, 2)
        pygame.draw.rect(screen, WHITE, RIGHT_AREA, 2)
        # 绘制 place 队列（左侧区域）
        draw_places(screen, gamestate.place, current_positions)
        #绘制 leader
        draw_leader(gamestate.leader)
        #绘制进度
        completed = 5 - len(gamestate.tasks)
        draw_progress_bar(completed, total=5)
        # 绘制任务表格（右侧区域）
        if gamestate.tasks:
            draw_task(screen, gamestate.tasks[0], task_position)
        else:
            complete_surf = big_font.render("工作完成！", True, GREEN)
            complete_rect = complete_surf.get_rect(center=RIGHT_AREA.center)
            screen.blit(complete_surf, complete_rect)
        # 绘制“下一回合”按钮
        draw_button(screen)
        # 检查游戏结束条件：例如所有 place 中的奇美拉均为 None（或不存活）
        if gamestate.end():
            draw_game_over(screen)
            # 可选择延迟退出或暂停（这里暂停显示游戏结束信息）
            pygame.display.flip()
            pygame.time.delay(5000)
            running = False
        pygame.display.flip()
    return gamestate

main()