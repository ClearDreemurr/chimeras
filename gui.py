import pygame
import sys
import os
import time

# 假设你已有的模块
# from gamestate import GameState
# from chimera import Chimera
# from task import Task

# ============ 基础设置 ============

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("奇美拉工作模拟")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
BLUE  = (100, 149, 237)
RED   = (220, 20, 60)
GREEN = (34, 139, 34)
ORANGE= (255, 140, 0)

# 字体定义
try:
    font = pygame.font.SysFont("SimHei", 20)
    big_font = pygame.font.SysFont("SimHei", 40)
except:
    font = pygame.font.SysFont("Arial", 20)
    big_font = pygame.font.SysFont("Arial", 40)

# 背景图片加载（如果有）
BG_PATH = os.path.join("background", "bg.jpg")
try:
    background_img = pygame.image.load(BG_PATH)
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

# 心形、锤子、闪电等图标的加载（如有需要）
# heart_icon = pygame.image.load("heart.png") # 仅示例
# hammer_icon = pygame.image.load("hammer.png")
# lightning_icon = pygame.image.load("lightning.png")

# ============ 界面布局坐标 ============

# 领队奇美拉框
LEADER_RECT = pygame.Rect(50, 50, 200, 150)

# 下方奇美拉区域（最多 5 只），预留一些坐标
CHIMERA_AREA_X = 50
CHIMERA_AREA_Y = HEIGHT - 180
CHIMERA_BOX_WIDTH = 120
CHIMERA_BOX_HEIGHT = 100
CHIMERA_SPACING = 30

# 右侧工作区域
TASK_RECT = pygame.Rect(WIDTH - 300, 50, 250, 500)
BUTTON_RECT = pygame.Rect(WIDTH - 250, 500, 100, 100)  # 工作按钮

# 进度条（正上方）显示当前完成工作数 / 5
PROGRESS_BAR_RECT = pygame.Rect(WIDTH//2 - 150, 10, 300, 30)

clock = pygame.time.Clock()

# ============ 一些辅助函数 ============

def load_chimera_image(chimera_class_name):
    """
    从chimera_pictures文件夹加载奇美拉图片，文件名与奇美拉类名相同，如 'Disservicer.jpg'
    如果加载失败则返回None
    """
    path = os.path.join("chimera_pictures", chimera_class_name + ".jpg")
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (CHIMERA_BOX_WIDTH, CHIMERA_BOX_HEIGHT - 20))
    except:
        return None

def load_task_image(task_class_name):
    """
    从works_pictures文件夹加载任务图片
    """
    path = os.path.join("works_pictures", task_class_name + ".jpg")
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (TASK_RECT.width - 20, 200))
    except:
        return None

def draw_background():
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(WHITE)

def draw_leader(leader):
    """
    领队奇美拉只显示名字和图片
    leader: 领队奇美拉对象
    """
    pygame.draw.rect(screen, BLACK, LEADER_RECT, 2)
    if leader:
        name_surf = font.render(leader.name, True, BLACK)
        name_rect = name_surf.get_rect(center=(LEADER_RECT.centerx, LEADER_RECT.top + 20))
        screen.blit(name_surf, name_rect)

        # 加载并绘制图片
        img = load_chimera_image(leader.__class__.__name__)
        if img:
            screen.blit(img, (LEADER_RECT.left+10, LEADER_RECT.top+40))

def draw_chimeras(chimeras):
    """
    在下方区域绘制最多5只奇美拉
    chimeras: [chimera1, chimera2, ...]
    """
    for i, chimera in enumerate(chimeras):
        x = CHIMERA_AREA_X + i * (CHIMERA_BOX_WIDTH + CHIMERA_SPACING)
        y = CHIMERA_AREA_Y
        rect = pygame.Rect(x, y, CHIMERA_BOX_WIDTH, CHIMERA_BOX_HEIGHT)
        color = BLACK
        # 如果奇美拉是即将工作或正在工作，可以设置color = ORANGE
        # 具体判断逻辑你可以根据 gamestate 的情况来写

        pygame.draw.rect(screen, color, rect, 2)

        # 显示名字
        name_surf = font.render(chimera.name, True, BLACK)
        screen.blit(name_surf, (x+5, y+5))

        # 显示图片
        img = load_chimera_image(chimera.__class__.__name__)
        if img:
            screen.blit(img, (x+ (CHIMERA_BOX_WIDTH - img.get_width())//2,
                              y+ (CHIMERA_BOX_HEIGHT - img.get_height())//2 + 10))

        # 显示精力(心形)与效率(锤子)
        heart_text = f"{chimera.energy}"  # + str(chimera.energy变化)
        efficiency_text = f"{chimera.efficiency}"
        heart_surf = font.render(heart_text, True, RED)
        eff_surf   = font.render(efficiency_text, True, BLUE)

        screen.blit(heart_surf, (x+5, y + CHIMERA_BOX_HEIGHT - 20))
        screen.blit(eff_surf, (x+CHIMERA_BOX_WIDTH - 25, y + CHIMERA_BOX_HEIGHT - 20))

def draw_task(task):
    """
    在右侧TASK_RECT区域绘制任务框
    """
    pygame.draw.rect(screen, BLACK, TASK_RECT, 2)
    # 假设task有 consumption(消耗), progress(进度), total_completion(完成度), name(可选)
    # 标题
    title_surf = font.render("工作", True, BLACK)
    screen.blit(title_surf, (TASK_RECT.centerx - title_surf.get_width()//2, TASK_RECT.top+10))

    # 消耗(闪电) + 进度/完成度
    cons_text = f"{task.consumption}"
    cons_surf = font.render(cons_text, True, ORANGE)
    screen.blit(cons_surf, (TASK_RECT.left+20, TASK_RECT.top+50))

    prog_text = f"{task.progress}/{task.total_completion}"
    prog_surf = font.render(prog_text, True, BLUE)
    screen.blit(prog_surf, (TASK_RECT.right - 70, TASK_RECT.top+50))

    # 任务图片
    img = load_task_image(task.__class__.__name__)
    if img:
        screen.blit(img, (TASK_RECT.centerx - img.get_width()//2, TASK_RECT.top+80))

    # 工作按钮(圆形)
    pygame.draw.circle(screen, ORANGE, (BUTTON_RECT.centerx, BUTTON_RECT.centery), 50)
    btn_text = font.render("工作", True, BLACK)
    btn_rect = btn_text.get_rect(center=BUTTON_RECT.center)
    screen.blit(btn_text, btn_rect)

    # 工作进度条(底部略微偏上一点)
    # 这里是任务自身进度条, 你也可以放在别处
    bar_rect = pygame.Rect(TASK_RECT.left+20, TASK_RECT.bottom-50, TASK_RECT.width-40, 20)
    pygame.draw.rect(screen, GRAY, bar_rect)
    fill_width = int(bar_rect.width * task.progress / task.total_completion)
    fill_rect = pygame.Rect(bar_rect.left, bar_rect.top, fill_width, bar_rect.height)
    pygame.draw.rect(screen, GREEN, fill_rect)

def draw_round_progress(turn, completed_work):
    """
    画面正上方正中间, 表示本回合已完成的工作数量 / 5
    """
    # 背景条
    pygame.draw.rect(screen, BLACK, (PROGRESS_BAR_RECT.x, PROGRESS_BAR_RECT.y, PROGRESS_BAR_RECT.width, PROGRESS_BAR_RECT.height), 2)
    # 填充
    fill_ratio = completed_work / 5
    fill_w = int(PROGRESS_BAR_RECT.width * fill_ratio)
    fill_rect = pygame.Rect(PROGRESS_BAR_RECT.x, PROGRESS_BAR_RECT.y, fill_w, PROGRESS_BAR_RECT.height)
    pygame.draw.rect(screen, GREEN, fill_rect)

    # 显示数字
    text = f"回合: {turn} | 工作: {completed_work}/5"
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=PROGRESS_BAR_RECT.center)
    screen.blit(text_surf, text_rect)

def main_gui_loop(gamestate):
    """
    这是一个示例的主GUI循环，你可以根据自己的逻辑和 main 函数做整合
    """
    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # 如果点击了工作按钮
                if BUTTON_RECT.collidepoint(mouse_pos):
                    # 调用 gamestate.update() 或者只进行一次奇美拉工作
                    gamestate.update()

        # 绘制背景
        draw_background()
        # 绘制领队(如果有)
        if hasattr(gamestate, "leader"):
            draw_leader(gamestate.leader)
        # 绘制下方奇美拉
        draw_chimeras(gamestate.chimeras)
        # 绘制任务
        if gamestate.tasks:
            draw_task(gamestate.tasks[0])
        # 绘制回合进度(例如 turn, completed_work)
        # completed_work = 5 - len(gamestate.tasks)
        # draw_round_progress(gamestate.turn, completed_work)

        pygame.display.update()

    pygame.quit()
    sys.exit()
