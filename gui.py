# gui.py
import pygame
import sys
from chimera import *  # 假设这些类定义在 chimera 模块中
from task import Task                   # 任务类
from gamestate import GameState
from place import place

chimeras = [AbsenteeFreak(), AbsenteeMaster(), BadTempered(), ToughCookie(), Onlooker()]
tasks = Task().turn_task(1)
leader = CareerStandout()


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
MOVE_SPEED = 5

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

# --- 获取 gamestate 对象 ---
gamestate = GameState(chimeras, tasks, leader)

# 初始计算位置
target_positions = compute_place_positions(gamestate.place)
current_positions = [pos[:] for pos in target_positions]
task_position = compute_task_position()

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
    
def draw_skill_box(chimera, rect):
    # 定义文本框宽度和高度，可以与 rect 相同或者稍宽
    box_width = rect.width + 20
    box_height = 30
    box_x = rect.centerx - box_width // 2
    box_y = rect.top - box_height - 5  # 在上方 5 像素处
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    
    # 创建半透明表面
    s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    s.fill((50,50,50,180))  # 灰色半透明背景
    screen.blit(s, (box_x, box_y))
    
    # 绘制技能文本
    skill_text = font.render(chimera.skill_text, True, WHITE)
    text_rect = skill_text.get_rect(center=(box_rect.centerx, box_rect.centery))
    screen.blit(skill_text, text_rect)


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

def show_changes(obj, amount, attribute):
    """
    根据对象 obj 和属性名称 attribute 定位显示区域，
    在该区域上方显示浮动数字（amount），停顿 1 秒后自动消失。
    参数：
      obj: 奇美拉对象或任务对象
      amount: 本次改变的数值（可正可负）
      attribute: 字符串，表示属性，如 "energy", "efficiency", "progress"
    """
    # 默认显示位置
    display_pos = (0, 0)
    
    # 如果对象有 place 属性（即为奇美拉对象）
    if hasattr(obj, "place") and obj.place is not None:
        # 在 gamestate.place 中寻找这个 place 的索引
        index = None
        for idx, p in enumerate(gamestate.place):
            if p == obj.place:
                index = idx
                break
        if index is not None:
            # 取出当前显示的矩形位置
            pos = current_positions[index]
            # 计算浮动数字显示位置，取矩形的中心上方 15 像素
            display_pos = (pos[0] + PLACE_WIDTH // 2, pos[1] - 15)
    else:
        # 如果对象没有 place 属性，假设它是任务对象，使用 task_position
        display_pos = (task_position[0] + TASK_WIDTH // 2, task_position[1] - 15)
    
    # 绘制浮动数字：构造显示文本，例如 "+2" 或 "-3"
    change_text = f"{amount:+}"
    # 创建一个临时表面，使用大字体显示
    temp_surf = big_font.render(change_text, True, RED)
    temp_rect = temp_surf.get_rect(center=display_pos)
    
    # 为实现显示一秒效果，可以先在屏幕上绘制后调用 pygame.time.delay(1000)
    # 保存当前屏幕，绘制数字，然后等待 1 秒，再恢复背景（这里较为简化）
    screen.blit(temp_surf, temp_rect)
    pygame.display.update()
    pygame.time.delay(1000)

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


# --- 主循环 ---
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
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
        pygame.time.delay(2000)
        running = False
    
    pygame.display.flip()

pygame.quit()
sys.exit()
