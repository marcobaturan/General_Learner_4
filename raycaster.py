"""
Wolfenstein-style raycasting renderer
Based on python-doom implementation
"""

import math
import pygame
import os
from constants import *


# Texture caching
_texture_cache = None
_texture_loaded = False


def _load_textures():
    """Load wall textures once at startup."""
    global _texture_cache, _texture_loaded
    if _texture_loaded:
        return _texture_cache

    _texture_cache = []
    try:
        assets_path = os.path.join(os.path.dirname(__file__), "assets")
        for i in range(1, 6):
            tex_path = os.path.join(assets_path, f"{i}.png")
            tex = pygame.image.load(tex_path).convert()
            tex = pygame.transform.scale(tex, (256, 256))
            _texture_cache.append(tex)
        print(f"Loaded {len(_texture_cache)} textures")
    except Exception as e:
        print(f"Texture load failed: {e}, using fallback")
        # Create fallback texture
        tex = pygame.Surface((256, 256))
        for y in range(256):
            for x in range(256):
                if y % 16 < 2:
                    tex.set_at((x, y), (60, 60, 60))
                else:
                    gray = 100 + ((x + y) % 16) * 3
                    tex.set_at((x, y), (gray, gray, gray))
        _texture_cache = [tex] * 5

    _texture_loaded = True
    return _texture_cache


def draw_raycast_view(
    screen, rect, robot, env, learner=None, other_bot=None, active_bot=1
):
    """Wolfenstein-style 3D raycasting with proper DDA algorithm."""
    import math

    # Load textures once
    textures = _load_textures()
    tex = textures[0]  # Use first texture
    tex_size = 256

    # Clear background
    pygame.draw.rect(screen, BLACK, rect)

    # Draw ceiling gradient
    ceiling_color = (15, 15, 20)
    pygame.draw.rect(
        screen, ceiling_color, (rect.x, rect.y, rect.width, rect.height // 2)
    )

    # Draw floor
    floor_color = (25, 25, 30)
    pygame.draw.rect(
        screen,
        floor_color,
        (rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2),
    )

    pygame.draw.rect(screen, CYAN, rect, 2)

    # Player direction
    if robot.direction == DIR_N:
        dir_x, dir_y = 0, -1
        plane_x, plane_y = 0.66, 0
    elif robot.direction == DIR_E:
        dir_x, dir_y = 1, 0
        plane_x, plane_y = 0, 0.66
    elif robot.direction == DIR_S:
        dir_x, dir_y = 0, 1
        plane_x, plane_y = -0.66, 0
    else:  # DIR_W
        dir_x, dir_y = -1, 0
        plane_x, plane_y = 0, -0.66

    # Player position
    pos_x = robot.x + 0.5
    pos_y = robot.y + 0.5

    # Raycasting params
    fov = math.pi / 3
    num_rays = rect.width // 4  # Lower for performance
    delta_angle = fov / num_rays
    col_width = rect.width // num_rays

    # Start angle
    ray_angle = -fov / 2

    mirror_visible = False

    for ray_id in range(num_rays):
        # Calculate ray direction
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        # Which box of the map we're in
        map_x = int(pos_x)
        map_y = int(pos_y)

        # Length of ray from one x or y-side to next x or y-side
        if ray_dir_x != 0:
            delta_dist_x = abs(1 / ray_dir_x)
        else:
            delta_dist_x = 1e30

        if ray_dir_y != 0:
            delta_dist_y = abs(1 / ray_dir_y)
        else:
            delta_dist_y = 1e30

        # Step direction and initial distance
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1

        if ray_dir_x >= 0:
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x
        else:
            side_dist_x = (pos_x - map_x) * delta_dist_x

        if ray_dir_y >= 0:
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y
        else:
            side_dist_y = (pos_y - map_y) * delta_dist_y

        # DDA algorithm
        hit = False
        hit_side = 0
        max_steps = 20

        for _ in range(max_steps):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                hit_side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                hit_side = 1

            # Check bounds and hit
            if 0 <= map_x < GRID_W and 0 <= map_y < GRID_H:
                obj = env.get_at(map_x, map_y)
                if obj == WALL_ID:
                    hit = True
                    break
                if other_bot and map_x == other_bot.x and map_y == other_bot.y:
                    hit = True
                    hit_side = 2  # Other bot
                    break
                if obj == MIRROR_ID:
                    hit = True
                    mirror_visible = True
                    break
            else:
                hit = True
                break

        # Calculate perpendicular distance (fix fisheye)
        if hit_side == 0:
            perp_dist = (
                (map_x - pos_x + (1 - step_x) / 2) / ray_dir_x
                if ray_dir_x != 0
                else 1e30
            )
        elif hit_side == 1:
            perp_dist = (
                (map_y - pos_y + (1 - step_y) / 2) / ray_dir_y
                if ray_dir_y != 0
                else 1e30
            )
        else:
            perp_dist = min(side_dist_x, side_dist_y)

        perp_dist = perp_dist * math.cos(ray_angle)

        # Calculate wall height
        if perp_dist > 0.01:
            line_height = int(rect.height / perp_dist)
        else:
            line_height = rect.height

        # Calculate draw range
        draw_start = -line_height // 2 + rect.height // 2
        if draw_start < 0:
            draw_start = 0
        draw_end = line_height // 2 + rect.height // 2
        if draw_end >= rect.height:
            draw_end = rect.height - 1

        # Calculate texture X coordinate
        if hit_side == 0:
            wall_x = pos_y + perp_dist * ray_dir_y
        elif hit_side == 1:
            wall_x = pos_x + perp_dist * ray_dir_x
        else:
            wall_x = 0.5

        wall_x -= math.floor(wall_x)
        tex_x = int(wall_x * tex_size)

        if hit_side == 0 and ray_dir_x > 0:
            tex_x = tex_size - tex_x - 1
        if hit_side == 1 and ray_dir_y < 0:
            tex_x = tex_size - tex_x - 1

        # Calculate brightness
        brightness = max(30, 255 - int(perp_dist * 20))
        if hit_side == 1:
            brightness = int(brightness * 0.7)

        # Draw wall column with texture
        if hit_side < 2 and textures:
            try:
                tex_col = tex.subsurface((tex_x, 0, 1, tex_size))
                scaled = pygame.transform.scale(
                    tex_col, (col_width, draw_end - draw_start)
                )

                # Apply brightness
                arr = pygame.PixelArray(scaled)
                for x in range(scaled.get_width()):
                    for y in range(scaled.get_height()):
                        c = scaled.get_at((x, y))
                        new_c = (
                            max(0, min(255, int(c[0] * brightness // 255))),
                            max(0, min(255, int(c[1] * brightness // 255))),
                            max(0, min(255, int(c[2] * brightness // 255))),
                        )
                        scaled.set_at((x, y), new_c)
                del arr

                screen.blit(scaled, (rect.x + ray_id * col_width, draw_start))
            except:
                color = (brightness, brightness, brightness)
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        rect.x + ray_id * col_width,
                        draw_start,
                        col_width,
                        draw_end - draw_start,
                    ),
                )
        else:
            # Other bot or fallback
            if hit_side == 2:
                if active_bot == 1:
                    color = (brightness, brightness // 2, 0)
                else:
                    color = (0, brightness // 2, brightness)
            else:
                color = (brightness, brightness, brightness)

            pygame.draw.rect(
                screen,
                color,
                (
                    rect.x + ray_id * col_width,
                    draw_start,
                    col_width,
                    draw_end - draw_start,
                ),
            )

        ray_angle += delta_angle

    # Draw mirror reflection
    if mirror_visible and learner:
        ref_x = rect.x + rect.width // 2 - 30
        ref_y = rect.y + rect.height // 2 - 40
        ref_w = 60
        ref_h = 70

        if active_bot == 1:
            reflection_body = (50, 80, 150)
            reflection_border = (80, 120, 200)
        else:
            reflection_body = (150, 80, 30)
            reflection_border = (200, 120, 50)

        pygame.draw.rect(screen, reflection_body, (ref_x, ref_y, ref_w, ref_h))
        pygame.draw.rect(screen, reflection_border, (ref_x, ref_y, ref_w, ref_h), 2)

        eye_y = ref_y + 20
        pygame.draw.circle(screen, WHITE, (ref_x + 18, eye_y), 6)
        pygame.draw.circle(screen, WHITE, (ref_x + ref_w - 18, eye_y), 6)
        pygame.draw.circle(screen, BLACK, (ref_x + 20, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (ref_x + ref_w - 16, eye_y), 2)

        nose_x = ref_x + ref_w // 2
        nose_y = ref_y + 45
        pygame.draw.circle(screen, (255, 50, 50), (nose_x, nose_y), 5)

        font = pygame.font.SysFont("Arial", 11, bold=True)
        id_str = str(robot.self_id)
        id_text = font.render(f"ID:{id_str}", True, (255, 150, 150))
        screen.blit(id_text, (ref_x + 5, ref_y + ref_h + 5))

    # HUD
    font = pygame.font.SysFont("Arial", 14)
    lbl = font.render(" POV - ROBOT VISION", True, WHITE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))
