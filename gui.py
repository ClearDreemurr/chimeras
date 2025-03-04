# gui.py
import pygame
import sys
from chimera import NormalChimera, Chimera
from task import Task
from gamestate import GameState

pygame.font.init()
# 如果需要显示中文，尝试加载支持中文的字体（例如系统字体“SimHei”）
try:
    font = pygame.font.SysFont("SimHei", 20)
    big_font = pygame.font.SysFont("SimHei", 40)
except Exception:
    font = pygame.font.SysFont("Arial", 20)
    big_font = pygame.font.SysFont("Arial", 40)

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

# 定义区域：左侧显示奇美拉队列，右侧显示任务
LEFT_AREA = pygame.Rect(50, 50, WIDTH // 2 - 100, HEIGHT - 150)
RIGHT_AREA = pygame.Rect(WIDTH // 2 + 50, 50, WIDTH // 2 - 100, HEIGHT - 150)

# 定义按钮区域（例如底部中央放“下一回合”按钮）
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_RECT = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT)

# 定义奇美拉和任务的显示尺寸
CHIMERA_WIDTH = 120
CHIMERA_HEIGHT = 80
CHIMERA_SPACING = 20
TASK_WIDTH = 200
TASK_HEIGHT = 100

# 动画移动速度（像素/帧）
MOVE_SPEED = 5

# 从已有模块中创建 gamestate 对象
def create_game_state():
    # 你的实际创建方式
    turn = 1
    chimeras = [NormalChimera(), Chimera("内卷王", 8, 5), NormalChimera()] 
    tasks = Task().turn_task(1)
    return GameState(chimeras, tasks)

gamestate = create_game_state()

# GUI层负责计算元素的位置，不依赖 gamestate 内保存的位置信息
def compute_chimera_positions(chimeras):
    """
    根据奇美拉数量计算每只奇美拉在左侧区域内的显示位置，
    排列顺序为从右到左，gamestate.chimeras[0] 显示在最右侧
    """
    positions = []
    for idx in range(len(chimeras)):
        x = LEFT_AREA.right - (CHIMERA_WIDTH + CHIMERA_SPACING) * (idx + 1)
        y = LEFT_AREA.centery - CHIMERA_HEIGHT // 2
        positions.append([x, y])
    return positions

def compute_task_position():
    """
    任务表格固定显示在右侧区域中央
    """
    x = RIGHT_AREA.centerx - TASK_WIDTH // 2
    y = RIGHT_AREA.centery - TASK_HEIGHT // 2
    return [x, y]

chimera_positions = compute_chimera_positions(gamestate.chimeras)
task_position = compute_task_position()

def draw_chimeras(screen, chimeras, positions):
    for idx, chimera in enumerate(chimeras):
        pos = positions[idx]
        rect = pygame.Rect(pos[0], pos[1], CHIMERA_WIDTH, CHIMERA_HEIGHT)
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        # 绘制名字（确保名字是字符串，若字体不支持中文，请尝试其它字体）
        name_surf = font.render(str(chimera.name), True, BLACK)
        name_rect = name_surf.get_rect(center=(rect.centerx, rect.top + 15))
        screen.blit(name_surf, name_rect)
        # 绘制工作效率（左下角）
        eff_surf = font.render(f"效:{chimera.efficiency}", True, BLUE)
        eff_rect = eff_surf.get_rect(bottomleft=(rect.left+5, rect.bottom-5))
        screen.blit(eff_surf, eff_rect)
        # 绘制精力（右下角）
        energy_surf = font.render(f"活:{chimera.energy}", True, RED)
        energy_rect = energy_surf.get_rect(bottomright=(rect.right-5, rect.bottom-5))
        screen.blit(energy_surf, energy_rect)

def draw_task(screen, task, pos):
    rect = pygame.Rect(pos[0], pos[1], TASK_WIDTH, TASK_HEIGHT)
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    title_surf = font.render("工作", True, BLACK)
    title_rect = title_surf.get_rect(center=(rect.centerx, rect.top+15))
    screen.blit(title_surf, title_rect)
    cons_surf = font.render(f"消耗:{task.consumption}", True, BLUE)
    cons_rect = cons_surf.get_rect(bottomleft=(rect.left+5, rect.bottom-5))
    screen.blit(cons_surf, cons_rect)
    prog_surf = font.render(f"进度:{task.progress}/{task.completion}", True, RED)
    prog_rect = prog_surf.get_rect(bottomright=(rect.right-5, rect.bottom-5))
    screen.blit(prog_surf, prog_rect)

def draw_button(screen):
    pygame.draw.rect(screen, GREEN, BUTTON_RECT)
    btn_text = font.render("下一回合", True, BLACK)
    btn_rect = btn_text.get_rect(center=BUTTON_RECT.center)
    screen.blit(btn_text, btn_rect)

clock = pygame.time.Clock()

# 主循环：现在改为手动点击“下一回合”按钮触发 gamestate.update()
running = True
while running:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # 判断是否点击“下一回合”按钮
            if BUTTON_RECT.collidepoint(mouse_pos):
                print("点击了下一回合按钮")
                gamestate.update()  # 更新一回合（包含准备、工作和结算阶段）
                # 更新奇美拉队列显示位置（如果有奇美拉退场）
                chimera_positions = compute_chimera_positions(gamestate.chimeras)
                # 更新任务位置（如果任务切换，动画效果可扩展）
                task_position = compute_task_position()
            else:
                # 判断点击奇美拉显示技能详情
                for idx, pos in enumerate(chimera_positions):
                    rect = pygame.Rect(pos[0], pos[1], CHIMERA_WIDTH, CHIMERA_HEIGHT)
                    if rect.collidepoint(mouse_pos):
                        print(f"点击了 {gamestate.chimeras[idx].name}，显示技能详情……")
                        # 此处可以调用弹窗函数显示详细技能信息
                        break

    screen.fill(WHITE)
    # 绘制区域边框
    pygame.draw.rect(screen, BLACK, LEFT_AREA, 2)
    pygame.draw.rect(screen, BLACK, RIGHT_AREA, 2)
    # 绘制奇美拉队列
    draw_chimeras(screen, gamestate.chimeras, chimera_positions)
    # 绘制任务表格或“工作完成”提示
    if gamestate.tasks:
        draw_task(screen, gamestate.tasks[0], task_position)
    else:
        complete_surf = big_font.render("工作完成！", True, GREEN)
        complete_rect = complete_surf.get_rect(center=RIGHT_AREA.center)
        screen.blit(complete_surf, complete_rect)
    # 绘制“下一回合”按钮
    draw_button(screen)
    
    pygame.display.flip()

pygame.quit()
sys.exit()
