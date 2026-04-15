import pygame
from constants import *

# Check if pygame is initialized (for testing without display)
_pygame_init = hasattr(pygame, "init")


def create_robot_icon(size, color=BLUE):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, color, (size // 4, size // 4, size // 2, size // 2))
    # Head
    pygame.draw.rect(icon, color, (size // 3, size // 8, size // 3, size // 4))
    # Eyes
    pygame.draw.circle(icon, WHITE, (size // 3 + 2, size // 8 + 4), 2)
    pygame.draw.circle(icon, WHITE, (size // 3 * 2 - 2, size // 8 + 4), 2)
    return icon


def create_battery_icon(size):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, GREEN, (size // 4, size // 4, size // 2, size // 2))
    # Cap
    pygame.draw.rect(icon, GRAY, (size // 3 + 2, size // 8, size // 4, size // 8))
    # Symbol
    pygame.draw.line(
        icon, BLACK, (size // 2 - 4, size // 2), (size // 2 + 4, size // 2), 2
    )
    pygame.draw.line(
        icon, BLACK, (size // 2, size // 2 - 4), (size // 2, size // 2 + 4), 2
    )
    return icon


def create_wall_icon(size):
    icon = pygame.Surface((size, size))
    icon.fill(GRAY)
    # Small stone details
    for i in range(4):
        x = (i * 7) % size
        y = (i * 11) % size
        pygame.draw.rect(icon, DARK_GRAY, (x, y, 4, 4))
    return icon


def create_mirror_icon(size):
    """Creates a light purple reflective surface icon for the mirror."""
    icon = pygame.Surface((size, size))
    # Light purple/magenta for mirror surface
    mirror_color = (180, 140, 200)
    icon.fill(mirror_color)
    # Add reflective border
    pygame.draw.rect(icon, (220, 180, 240), (0, 0, size, size), 2)
    # Add "shiny" diagonal line
    pygame.draw.line(icon, (255, 255, 255), (size // 4, 0), (size, size * 3 // 4), 1)
    return icon


def create_reset_button_icon(size):
    """Creates a bright green reset button icon (psychosis cure tile)."""
    icon = pygame.Surface((size, size))
    # Bright green fill (distinct from battery green)
    icon.fill((50, 200, 50))
    # Darker green border
    pygame.draw.rect(icon, (30, 150, 30), (0, 0, size, size), 3)
    # Center circle (button appearance)
    pygame.draw.circle(icon, (30, 150, 30), (size // 2, size // 2), size // 4)
    # Inner circle
    pygame.draw.circle(icon, (80, 220, 80), (size // 2, size // 2), size // 6)
    return icon


class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 18)
        self._text_surface = self.font.render(text, True, text_color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_rect = self._text_surface.get_rect(center=self.rect.center)
        screen.blit(self._text_surface, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class TextBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.font = pygame.font.SysFont("Arial", 18)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                self.text += event.unicode
        return False

    def draw(self, screen):
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_surf = self.font.render(self.text, True, BLACK)
        screen.blit(txt_surf, (self.rect.x + 5, self.rect.y + 10))


def draw_scaled_plot(screen, rect, data, color, title, label_y):
    """
    Draws a simple line chart within a given Rect based on a list of numeric data.
    """
    pygame.draw.rect(screen, (20, 20, 25), rect)  # Dark background for the chart
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)  # Container border

    font = pygame.font.SysFont("Arial", 14)
    tit_surf = font.render(title, True, WHITE)
    screen.blit(tit_surf, (rect.x + 5, rect.y + 5))

    if len(data) < 2:
        return

    # Scaling logic
    max_val = max(data) if max(data) > 0 else 1
    min_val = min(data)

    points = []
    margin = 20
    plot_w = rect.width - (margin * 2)
    plot_h = rect.height - (margin * 2) - 10

    for i, val in enumerate(data):
        x = rect.x + margin + (i / (len(data) - 1)) * plot_w
        # Invert Y for screen coordinates
        y = (
            rect.y
            + rect.height
            - margin
            - ((val - min_val) / (max_val - min_val + 1e-5)) * plot_h
        )
        points.append((x, y))

    if len(points) >= 2:
        pygame.draw.lines(screen, color, False, points, 2)

    # Draw Y labels
    min_surf = font.render(str(int(min_val)), True, DARK_GRAY)
    max_surf = font.render(str(int(max_val)), True, DARK_GRAY)
    screen.blit(min_surf, (rect.x + 5, rect.y + rect.height - 18))
    screen.blit(max_surf, (rect.x + 5, rect.y + 20))


def draw_resource_monitor(screen, rect, mem_data, cpu_data):
    """
    Draws a resource monitor showing memory (MB) and CPU (%) usage over time.
    """
    pygame.draw.rect(screen, (20, 20, 25), rect)
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)

    font = pygame.font.SysFont("Arial", 14)
    tit_surf = font.render("RESOURCE MONITOR", True, WHITE)
    screen.blit(tit_surf, (rect.x + 5, rect.y + 5))

    if len(mem_data) < 2:
        return

    # Memory line (blue)
    max_mem = max(mem_data) if max(mem_data) > 0 else 1
    plot_w = rect.width - 40
    plot_h = rect.height - 30
    margin_x = 20
    margin_y = 15

    mem_points = []
    for i, val in enumerate(mem_data):
        x = rect.x + margin_x + (i / (len(mem_data) - 1)) * plot_w
        y = rect.y + rect.height - margin_y - (val / max_mem) * plot_h
        mem_points.append((x, y))

    if len(mem_points) >= 2:
        pygame.draw.lines(screen, BLUE, False, mem_points, 2)

    # CPU line (orange)
    max_cpu = max(cpu_data) if max(cpu_data) > 0 else 1
    cpu_points = []
    for i, val in enumerate(cpu_data):
        x = rect.x + margin_x + (i / (len(cpu_data) - 1)) * plot_w
        y = rect.y + rect.height - margin_y - (val / max_cpu) * plot_h
        cpu_points.append((x, y))

    if len(cpu_points) >= 2:
        pygame.draw.lines(screen, ORANGE, False, cpu_points, 2)

    # Legend
    leg_y = rect.y + rect.height - 12
    mem_leg = font.render("Mem (MB)", True, BLUE)
    cpu_leg = font.render("CPU (%)", True, ORANGE)
    screen.blit(mem_leg, (rect.x + 5, leg_y))
    screen.blit(cpu_leg, (rect.x + 80, leg_y))


def draw_mini_perception(screen, x, y, size, fuzzy_perc_id):
    """Renders a simplified view of the fuzzy perception vector."""
    import json

    pygame.draw.rect(screen, BLACK, (x, y, size, size))
    pygame.draw.rect(screen, DARK_GRAY, (x, y, size, size), 1)

    font = pygame.font.SysFont("Arial", 10)

    # Handle action nodes (fallback visualization)
    if fuzzy_perc_id and fuzzy_perc_id.startswith("ACTION_"):
        action_num = fuzzy_perc_id.replace("ACTION_", "")
        action_names = {0: "A0", 1: "A1", 2: "A2", 3: "A3"}
        label = action_names.get(int(action_num), f"A{action_num}")
        txt = font.render(label, True, YELLOW)
        screen.blit(txt, (x + 2, y + 12))
        return

    try:
        vector = json.loads(fuzzy_perc_id)
        # Show top 2-3 features as text
        for i, feat in enumerate(vector[:3]):
            txt = font.render(feat[:15], True, WHITE)
            screen.blit(txt, (x + 2, y + 2 + i * 10))
    except (json.JSONDecodeError, KeyError, TypeError):
        pass


def draw_territory_map(screen, rect, territory_data):
    """Draws the global world map from visited (x, y) coordinates."""
    pygame.draw.rect(screen, (10, 10, 15), rect)
    pygame.draw.rect(screen, BLUE, rect, 2)

    if not territory_data:
        font = pygame.font.SysFont("Arial", 18)
        msg = font.render("No territory explored yet.", True, GRAY)
        screen.blit(msg, (rect.centerx - 100, rect.centery))
        return

    # Scaling cell size to fit the rect
    cell_w = rect.width / GRID_W
    cell_h = rect.height / GRID_H

    for entry in territory_data:
        tx, ty = entry["x"], entry["y"]
        visits = entry["visits"]
        importance = entry.get("importance", 1.0)

        draw_x = rect.x + tx * cell_w
        draw_y = rect.y + ty * cell_h

        # Color based on visits/importance
        intensity = min(255, 50 + visits * 20)
        color = (
            (0, intensity // 2, intensity)
            if importance <= 1.0
            else (intensity, intensity // 2, 0)
        )

        pygame.draw.rect(screen, color, (draw_x, draw_y, cell_w, cell_h))
        pygame.draw.rect(screen, (0, 0, 40), (draw_x, draw_y, cell_w, cell_h), 1)

    # Label
    font = pygame.font.SysFont("Arial", 14)
    lbl = font.render("GLOBAL TERRITORY MAP", True, WHITE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))


def draw_situational_network(
    screen, rect, nodes, edges, memory_obj=None, cmd_cache=None
):
    """Draws the situational graph as a relational network with symbolic tokens."""
    import math

    pygame.draw.rect(screen, (15, 15, 20), rect)
    pygame.draw.rect(screen, CYAN, rect, 2)

    if not nodes:
        return

    center_x, center_y = rect.center
    radius = min(rect.width, rect.height) // 3
    node_pos = {}

    font = pygame.font.SysFont("Arial", 12)

    # Pre-build command cache if not provided
    if cmd_cache is None and memory_obj:
        cmd_cache = {}
        try:
            cur = memory_obj.conn.cursor()
            cur.execute("SELECT id, value FROM conceptual_ids")
            for row in cur.fetchall():
                cmd_cache[row["id"]] = row["value"]
        except sqlite3.Error:
            pass

    for i, node_id in enumerate(nodes):
        angle = (i / len(nodes)) * 2 * math.pi
        nx = center_x + radius * math.cos(angle)
        ny = center_y + radius * math.sin(angle)
        node_pos[node_id] = (nx, ny)

    # Draw edges with labels
    for s1, action, s2, weight, cmd_id in edges:
        if s1 in node_pos and s2 in node_pos:
            start, end = node_pos[s1], node_pos[s2]
            color = (max(50, min(255, 100 + int(weight * 20))), 100, 200)
            pygame.draw.line(screen, color, start, end, 2)

            # Midpoint label for action/concept
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2

            label_text = f"A:{action}"
            if cmd_id and cmd_cache:
                val = cmd_cache.get(cmd_id)
                if val:
                    label_text = f"'{val}'" if val != " " else "[SPACE]"

            lbl = font.render(label_text, True, YELLOW)
            screen.blit(lbl, (mid_x, mid_y))

    # Draw nodes as mini-perceptions
    node_size = 40
    for node_id, (nx, ny) in node_pos.items():
        draw_mini_perception(
            screen, nx - node_size // 2, ny - node_size // 2, node_size, node_id
        )


def draw_raycast_view(
    screen, rect, robot, env, learner=None, other_bot=None, active_bot=1
):
    """
    Renders a pseudo-3D scene using Ray Casting from the robot's perspective.
    GL5.1 DUAL-POV: Now shows both robots' POVs stacked.
    """
    import math

    # Divide rect into two halves
    half_h = rect.height // 2
    rect1 = pygame.Rect(rect.x, rect.y, rect.width, half_h - 2)
    rect2 = pygame.Rect(rect.x, rect.y + half_h + 2, rect.width, half_h - 2)

    # Draw POV for each robot
    draw_single_pov(screen, rect1, robot, env, learner, other_bot, 1, ORANGE)
    draw_single_pov(screen, rect2, other_bot, env, learner, robot, 2, CYAN)


def draw_single_pov(
    screen, rect, robot, env, learner, other_bot, bot_num, border_color
):
    """
    Draws a single POV view for one robot.
    bot_num: 1 or 2
    border_color: Color for border (Bot1=ORANGE, Bot2=CYAN)
    """
    import math

    if robot is None:
        pygame.draw.rect(screen, BLACK, rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        font = pygame.font.SysFont("Arial", 10)
        lbl = font.render(f"Bot{bot_num}: N/A", True, border_color)
        screen.blit(lbl, (rect.x + 5, rect.y + rect.height // 2 - 10))
        return

    pygame.draw.rect(screen, BLACK, rect)

    ground_y = rect.y + rect.height // 2
    ground_h = rect.height // 2
    pygame.draw.rect(screen, (25, 25, 30), (rect.x, ground_y, rect.width, ground_h))
    pygame.draw.rect(screen, border_color, rect, 1)

    base_angle = 0
    if robot.direction == DIR_N:
        base_angle = -math.pi / 2
    elif robot.direction == DIR_E:
        base_angle = 0
    elif robot.direction == DIR_S:
        base_angle = math.pi / 2
    elif robot.direction == DIR_W:
        base_angle = math.pi

    fov = math.pi / 3
    half_fov = fov / 2
    num_rays = rect.width // 2
    delta_angle = fov / num_rays
    col_width = rect.width // num_rays
    ray_angle = base_angle - half_fov

    mirror_visible = False
    mirror_distance = 0

    for i in range(num_rays):
        step = 0.08
        max_dist = 12.0
        dist = 0
        hit = False
        hit_obj = EMPTY_ID
        hit_side = 0

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        while dist < max_dist and not hit:
            dist += step
            rx = robot.x + 0.5 + cos_a * dist
            ry = robot.y + 0.5 + sin_a * dist

            if 0 <= rx < GRID_W and 0 <= ry < GRID_H:
                obj = env.get_at(int(rx), int(ry))
                if other_bot and int(rx) == other_bot.x and int(ry) == other_bot.y:
                    hit = True
                    hit_obj = 99
                elif obj == WALL_ID or obj == BATTERY_ID:
                    hit = True
                    hit_obj = obj
                    dx = abs(rx - round(rx))
                    dy = abs(ry - round(ry))
                    hit_side = 1 if dy < dx else 0
                elif obj == MIRROR_ID:
                    if dist < max_dist:
                        hit = True
                        hit_obj = MIRROR_ID
                        if not mirror_visible:
                            mirror_visible = True
                            mirror_distance = dist
            else:
                hit = True
                hit_obj = WALL_ID
                hit_side = 0

        dist = dist * math.cos(ray_angle - base_angle)
        proj_h = (1.0 / (dist + 0.1)) * rect.height * 0.8
        if proj_h > rect.height:
            proj_h = rect.height

        y1 = rect.y + rect.height // 2 - proj_h // 2
        y2 = rect.y + rect.height // 2 + proj_h // 2

        brightness = max(0, 255 - int(dist * 20))
        if hit_side == 1:
            brightness = int(brightness * 0.7)

        color = (brightness, brightness, brightness)
        if hit_obj == BATTERY_ID:
            color = (0, brightness, 0)
        elif hit_obj == MIRROR_ID:
            color = (100, 80, 150)
        elif hit_obj == 99:
            if bot_num == 1:
                color = (brightness, brightness // 2, 0)
            else:
                color = (0, brightness // 2, brightness)

        pygame.draw.rect(
            screen, color, (rect.x + i * col_width, y1, col_width, y2 - y1)
        )
        ray_angle += delta_angle

    if mirror_visible and learner and mirror_distance < 6:
        ref_x = rect.x + rect.width // 2 - 20
        ref_y = rect.y + rect.height // 2 - 25
        ref_w = 40
        ref_h = 45

        if bot_num == 1:
            reflection_body = (50, 80, 150)
            reflection_border = (80, 120, 200)
        else:
            reflection_body = (150, 80, 30)
            reflection_border = (200, 120, 50)

        pygame.draw.rect(screen, reflection_body, (ref_x, ref_y, ref_w, ref_h))
        pygame.draw.rect(screen, reflection_border, (ref_x, ref_y, ref_w, ref_h), 2)

        eye_y = ref_y + 12
        pygame.draw.circle(screen, WHITE, (ref_x + 12, eye_y), 4)
        pygame.draw.circle(screen, WHITE, (ref_x + ref_w - 12, eye_y), 4)
        pygame.draw.circle(screen, BLACK, (ref_x + 13, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (ref_x + ref_w - 11, eye_y), 2)

        nose_x = ref_x + ref_w // 2
        nose_y = ref_y + 28
        pygame.draw.circle(screen, (255, 50, 50), (nose_x, nose_y), 4)

        font = pygame.font.SysFont("Arial", 9, bold=True)
        id_surf = font.render(f"Bot{bot_num}", True, (255, 150, 150))
        screen.blit(id_surf, (ref_x + 5, ref_y + ref_h + 3))

    font = pygame.font.SysFont("Arial", 10, bold=True)
    lbl = font.render(f"Bot{bot_num} POV", True, border_color)
    screen.blit(lbl, (rect.x + 5, rect.y + 2))


def draw_inferences_window(screen, rect, learner, robot=None, gwt_result=None):
    """
    GL5.1: Draws mental state. Positioned below maze grid.
    """
    pygame.draw.rect(screen, (20, 20, 25), rect)
    pygame.draw.rect(screen, ORANGE, rect, 2)

    font_title = pygame.font.SysFont("Arial", 11, bold=True)
    font_body = pygame.font.SysFont("Arial", 9)
    font_small = pygame.font.SysFont("Arial", 8)

    lbl = font_title.render("MENTAL STATES", True, ORANGE)
    screen.blit(lbl, (rect.x + 5, rect.y + 2))

    y1 = rect.y + 16
    y2 = rect.y + 16
    col1_x = rect.x + 6
    col2_x = rect.x + rect.width // 2 + 3
    step = 10

    def sec1(title, color):
        nonlocal y1
        screen.blit(font_body.render(f"[{title}]", True, color), (col1_x, y1))
        y1 += step

    def sec2(title, color):
        nonlocal y2
        screen.blit(font_body.render(f"[{title}]", True, color), (col2_x, y2))
        y2 += step

    def ln1(text, color=(200, 200, 200)):
        nonlocal y1
        screen.blit(font_small.render(text, True, color), (col1_x, y1))
        y1 += step

    def ln2(text, color=(200, 200, 200)):
        nonlocal y2
        screen.blit(font_small.render(text, True, color), (col2_x, y2))
        y2 += step

    # LEFT COLUMN
    sec1("DECISION", CYAN)
    inf_type = learner.last_inference_info.get("type", "N/A")[:15]
    ln1(f"Logic: {inf_type}", GREEN)

    # Activity tracking
    activity = learner.get_last_activity()
    last_cmd = activity.get("last_command")
    last_reinf = activity.get("last_reinforcement", 0)
    if last_cmd:
        ln1(f"Cmd: {last_cmd[:12]}", YELLOW)
    reinf_color = GREEN if last_reinf > 0 else (RED if last_reinf < 0 else DARK_GRAY)
    ln1(f"Reinf: {last_reinf:+d}", reinf_color)

    vic = learner.get_vicarious_status()
    sec1("VICARIOUS", LIGHT_ORANGE)
    mode = "IMT" if vic.get("in_imitating_mode") else "AUTO"
    sat = vic.get("saturation", 0)
    ln1(
        f"{mode} Sat:{sat}% Auto:{vic.get('autonomous_streak', 0)}",
        ORANGE if vic.get("in_imitating_mode") else GREEN,
    )

    hearing = learner.get_hearing_status()
    heard_now = hearing.get("heard_this_cycle", [])
    heard_str = heard_now[0][0] if heard_now else "-"
    sec1("HEARING", CYAN if heard_now else DARK_GRAY)
    ln1(
        f"Heard: {heard_str} Beliefs:{hearing.get('beliefs_count', 0)}",
        GREEN if heard_now else DARK_GRAY,
    )

    imag = learner.get_imagination_status()
    sec1(
        "IMAGINAT",
        PURPLE if imag.get("active") else (CYAN if imag.get("enabled") else DARK_GRAY),
    )
    ln1(
        f"{'ACTIVE' if imag.get('active') else 'IDLE'} Idle:{imag.get('idle_counter', 0)}",
        PURPLE if imag.get("active") else GREEN,
    )
    ln1(
        f"Prods:{imag.get('total_imagined', 0)}/{imag.get('total_productions', 0)} Conf:{imag.get('avg_confidence', 0):.2f}",
        PURPLE,
    )

    # RIGHT COLUMN
    mem = learner.memory if hasattr(learner, "memory") else None
    sec2("MEMORY", GREEN)
    if mem:
        rules = mem.get_rules(limit=1000)
        frames = mem.get_all_frames()
        objs = getattr(learner, "objective_values", {})
        goals = sum(1 for v in objs.values() if v >= 3)
        pains = sum(1 for v in objs.values() if v <= -3)
        ln2(f"Rules:{len(rules)} Frames:{len(frames)}", GREEN)
        ln2(f"Goals:{goals} Pains:{pains}", PURPLE)
    else:
        ln2("Memory: N/A", DARK_GRAY)

    sec2("HISTORY", YELLOW)
    hist = getattr(learner, "action_history", [])
    if hist:
        names = {0: "L", 1: "R", 2: "F", 3: "B"}
        recent = [names.get(a, "?") for a in hist[-4:]]
        ln2(f"Recent: {recent}", YELLOW)
    plan = getattr(learner, "active_plan", [])
    ln2(f"Plan: {plan if plan else '-'}", GREEN if plan else DARK_GRAY)

    if robot:
        sec2("HOMEOST", RED)
        hcolor = RED if robot.hunger > 80 else (ORANGE if robot.hunger > 50 else GREEN)
        ln2(f"Hung:{robot.hunger} Tired:{robot.tiredness}", hcolor)
        ln2(f"Score:{robot.score} ID:{getattr(robot, 'self_id', '?')}", CYAN)

    if mem:
        cog = mem.get_cognitive_stats()
        sec2("COGNITIVE", PURPLE)
        ln2(f"CogProds:{cog.get('total_productions', 0)}", PURPLE)
        ln2(f"HeardMem:{cog.get('total_heard_memories', 0)}", CYAN)
