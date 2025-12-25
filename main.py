import pygame
import hex_lib
import os
import random
import map_lib
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (30, 30, 30)
HEX_SIZE = 30
GRID_RADIUS = 5
HEX_BORDER_COLOR = (200, 200, 200)

TYPE_GRASS = 1
TYPE_WATER = 2
TYPE_DIRT = 3
TYPE_STONE = 4
TYPE_SAND = 5

COLORS = {
    TYPE_GRASS: (100, 255, 100), # Green
    TYPE_WATER: (50, 100, 255),  # Blue (Impassable)
    TYPE_DIRT: (150, 100, 50),   # Brown
    TYPE_STONE: (150, 150, 150), # Grey
    TYPE_SAND: (240, 230, 140)   # Sand
}

COSTS = {
    TYPE_GRASS: 1,
    TYPE_WATER: 999,
    TYPE_DIRT: 2,
    TYPE_STONE: 3,
    TYPE_SAND: 1
}

MP_PLAYER_MAX = 2
MP_AI_MAX = 1
WIN_SCORE = 2

SPRITES = {}

def generate_hex_grid(radius):
    hex_map = {}
    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        for r in range(r1, r2 + 1):
            hex_map[hex_lib.Hex(q, r)] = TYPE_GRASS
    return hex_map

def load_and_scale_sprite(path, size):
    if not os.path.exists(path):
        print(f"Warning: Sprite not found at {path}")
        return pygame.Surface(size)
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

def create_hex_surface(size, texture_path=None):
    width = int(hex_lib.math.sqrt(3) * size)
    height = int(2 * size)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    center = hex_lib.Point(width / 2, height / 2)
    layout = hex_lib.Layout(hex_lib.layout_pointy, hex_lib.Point(size, size), center)
    corners = hex_lib.polygon_corners(layout, hex_lib.Hex(0, 0))
    pixel_corners = [(c.x - center.x + width/2, c.y - center.y + height/2) for c in corners]

    pygame.draw.polygon(surface, (255, 255, 255, 255), pixel_corners)
    
    if texture_path and os.path.exists(texture_path):
        texture = pygame.image.load(texture_path).convert_alpha()
        tex_surf = pygame.transform.scale(texture, (width, height))
        tex_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return tex_surf
    
    return surface

def load_sprites():
    # Use consistent size with slight overlap
    s = HEX_SIZE + 1

    SPRITES[TYPE_GRASS] = create_hex_surface(s, texture_path=os.path.join("sprites", "tex_grass.png"))
    if not os.path.exists(os.path.join("sprites", "tex_grass.png")):
         SPRITES[TYPE_GRASS] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_grass.png"))

    SPRITES[TYPE_WATER] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_water.png"))
    SPRITES[TYPE_DIRT] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_dirt.png"))
    SPRITES[TYPE_STONE] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_stone.png"))
    SPRITES[TYPE_SAND] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_sand.png"))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hex Grid Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    
    load_sprites()

    # Setup Hex Layout
    origin = hex_lib.Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    layout = hex_lib.Layout(hex_lib.layout_pointy, hex_lib.Point(HEX_SIZE, HEX_SIZE), origin)

    # Create/Load Grid
    map_file = "level.map"
    if len(sys.argv) > 1:
        map_file = sys.argv[1]

    loaded_map = map_lib.load_map(map_file)
    if loaded_map:
        grid_hexes = loaded_map
    else:
        print(f"Could not load {map_file}, generating default grid.")
        grid_hexes = generate_hex_grid(GRID_RADIUS)
    
    # Load Sprites
    sprite_size = (int(HEX_SIZE * 1.5), int(HEX_SIZE * 1.5))
    player_sprite = load_and_scale_sprite(os.path.join("sprites", "spr_pikachu.png"), sprite_size)
    enemy_sprite = load_and_scale_sprite(os.path.join("sprites", "spr_ekans.png"), sprite_size)

    # Game State
    player_pos = hex_lib.Hex(0, 0)
    
    # Ensure player starts on valid tile
    if player_pos not in grid_hexes:
        if grid_hexes:
            player_pos = next(iter(grid_hexes))

    valid_starts = [h for h in grid_hexes if h != player_pos and grid_hexes[h] != TYPE_WATER]
    enemy_pos = random.choice(valid_starts) if valid_starts else hex_lib.Hex(1, -1)

    turn = "PLAYER" # PLAYER, AI, GAME_OVER
    player_mp = MP_PLAYER_MAX
    ai_mp = MP_AI_MAX
    
    player_brown_visited = set()
    ai_brown_visited = set()
    
    if grid_hexes.get(player_pos) == TYPE_DIRT:
        player_brown_visited.add(player_pos)
    if grid_hexes.get(enemy_pos) == TYPE_DIRT:
        ai_brown_visited.add(enemy_pos)

    winner = None

    running = True
    while running:
        # AI Turn Logic
        if turn == "AI":
            pygame.time.wait(500) # Small delay for visibility
            
            # Find valid moves
            neighbors = []
            for i in range(6):
                n = hex_lib.hex_neighbor(enemy_pos, i)
                if n in grid_hexes:
                    cost = COSTS.get(grid_hexes[n], 999)
                    if cost <= ai_mp and n != player_pos: # Avoid stacking for simplicity? Or allowed? Let's avoid.
                        neighbors.append((n, cost))
            
            if neighbors:
                target, cost = random.choice(neighbors)
                enemy_pos = target
                ai_mp -= cost
                if grid_hexes[enemy_pos] == TYPE_DIRT:
                    ai_brown_visited.add(enemy_pos)
                
                if len(ai_brown_visited) >= WIN_SCORE:
                    turn = "GAME_OVER"
                    winner = "AI"
            else:
                 ai_mp = 0 # Stuck, end turn

            if ai_mp <= 0 and turn != "GAME_OVER":
                turn = "PLAYER"
                player_mp = MP_PLAYER_MAX

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == "PLAYER":
                if event.button == 1: # Left click
                    mouse_pos = hex_lib.Point(event.pos[0], event.pos[1])
                    clicked_hex = hex_lib.pixel_to_hex(layout, mouse_pos)
                    
                    if clicked_hex in grid_hexes:
                        if hex_lib.hex_distance(player_pos, clicked_hex) == 1:
                            cost = COSTS.get(grid_hexes[clicked_hex], 999)
                            if player_mp >= cost and clicked_hex != enemy_pos:
                                player_pos = clicked_hex
                                player_mp -= cost
                                
                                if grid_hexes[player_pos] == TYPE_DIRT:
                                    player_brown_visited.add(player_pos)
                                
                                if len(player_brown_visited) >= WIN_SCORE:
                                    turn = "GAME_OVER"
                                    winner = "PLAYER"
                                elif player_mp <= 0:
                                    turn = "AI"
                                    ai_mp = MP_AI_MAX

        # Rendering
        screen.fill(BG_COLOR)

        # Draw Grid
        for h, t in grid_hexes.items():
            center = hex_lib.hex_to_pixel(layout, h)
            
            # Draw Sprite if available
            sprite = SPRITES.get(t)
            if sprite:
                rect = sprite.get_rect(center=(center.x, center.y))
                screen.blit(sprite, rect)
            else:
                corners = hex_lib.polygon_corners(layout, h)
                pixel_corners = [(c.x, c.y) for c in corners]
                color = COLORS.get(t, (255, 255, 255))
                pygame.draw.polygon(screen, color, pixel_corners)
                pygame.draw.polygon(screen, HEX_BORDER_COLOR, pixel_corners, 2)
            
            # Draw Characters
            if h == player_pos:
                rect = player_sprite.get_rect(center=(center.x, center.y))
                screen.blit(player_sprite, rect)
            
            if h == enemy_pos:
                rect = enemy_sprite.get_rect(center=(center.x, center.y))
                screen.blit(enemy_sprite, rect)

        # UI
        status_text = f"Turn: {turn} | Player MP: {player_mp} | P. Score: {len(player_brown_visited)} | AI Score: {len(ai_brown_visited)}"
        if turn == "GAME_OVER":
            status_text = f"GAME OVER! Winner: {winner}"
            
        text_surf = font.render(status_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
