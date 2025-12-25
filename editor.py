import pygame
import hex_lib
import map_lib
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (20, 20, 20)
HEX_SIZE = 30
GRID_RADIUS = 5
HEX_BORDER_COLOR = (200, 200, 200)

# Tile Types
TYPE_GRASS = 1
TYPE_WATER = 2
TYPE_DIRT = 3
TYPE_STONE = 4
TYPE_SAND = 5

COLORS = {
    TYPE_GRASS: (100, 255, 100), # Green
    TYPE_WATER: (50, 100, 255),  # Blue
    TYPE_DIRT: (150, 100, 50),   # Brown
    TYPE_STONE: (150, 150, 150), # Grey
    TYPE_SAND: (240, 230, 140)   # Sand
}

SPRITES = {}

def create_hex_surface(size, color=None, texture_path=None):
    # Create a surface that fits a hex with the given size (radius/side length)
    # Pointy top: width = sqrt(3) * size, height = 2 * size
    width = int(hex_lib.math.sqrt(3) * size)
    height = int(2 * size)
    
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Define hex corners relative to center of surface
    center = hex_lib.Point(width / 2, height / 2)
    layout = hex_lib.Layout(hex_lib.layout_pointy, hex_lib.Point(size, size), center)
    corners = hex_lib.polygon_corners(layout, hex_lib.Hex(0, 0))
    pixel_corners = [(c.x - center.x + width/2, c.y - center.y + height/2) for c in corners]

    # Draw the mask (White hex on transparent)
    pygame.draw.polygon(surface, (255, 255, 255, 255), pixel_corners)
    
    # If texture, mask it
    if texture_path and os.path.exists(texture_path):
        texture = pygame.image.load(texture_path).convert_alpha()
        # Scale texture to cover the hex surface (center crop or stretch)
        # Let's stretch to fill for simplicity
        texture = pygame.transform.scale(texture, (width, height))
        
        # Multiply blending: keep texture where mask is white, transparent where mask is transparent
        # Actually in pygame:
        # 1. Fill surface with white hex (already done)
        # 2. Blit texture with BLEND_RGBA_MULT? No, that requires texture to have alpha?
        # Better approach for masking in Pygame:
        # 1. Create solid hex on 'surface'
        # 2. lock surface? 
        # Easier: 
        # 1. Draw solid hex on 'mask_surf'
        # 2. Blit texture on 'final_surf'
        # 3. Blit 'mask_surf' on 'final_surf' with BLEND_RGBA_MIN or similar?
        
        # Standard Masking:
        # Surface has (0,0,0,0) everywhere.
        # Draw Polygon (255, 255, 255, 255).
        # Create Texture Surface.
        # Blit Surface onto Texture with BLEND_RGBA_MIN (keeps alpha of Surface) -> New Surface
        
        tex_surf = pygame.transform.scale(texture, (width, height))
        tex_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return tex_surf
        
    elif color:
        # Just color
        colored_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        colored_surf.fill(color)
        colored_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return colored_surf
    
    return surface

def load_sprites():
    # Use HEX_SIZE + padding? No, exact HEX_SIZE for seamless grid.
    # But usually a slight overlap (e.g. size + 1) helps with gaps.
    # Let's try exact size first.
    s = HEX_SIZE + 1
    
    # Use tex_grass.png if available, else tile_grass.png, etc.
    SPRITES[TYPE_GRASS] = create_hex_surface(s, texture_path=os.path.join("sprites", "tex_grass.png"))
    if not os.path.exists(os.path.join("sprites", "tex_grass.png")):
         SPRITES[TYPE_GRASS] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_grass.png"))
         
    SPRITES[TYPE_WATER] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_water.png"))
    SPRITES[TYPE_DIRT] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_dirt.png"))
    SPRITES[TYPE_STONE] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_stone.png"))
    SPRITES[TYPE_SAND] = create_hex_surface(s, texture_path=os.path.join("sprites", "tile_sand.png"))

def generate_hex_grid(radius):
    hex_map = {}
    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        for r in range(r1, r2 + 1):
            hex_map[hex_lib.Hex(q, r)] = TYPE_GRASS
    return hex_map

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hex Map Editor - [1-5: Paint] [S:Save] [L:Load]")
    clock = pygame.time.Clock()

    load_sprites()

    # Layout
    origin = hex_lib.Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    layout = hex_lib.Layout(hex_lib.layout_pointy, hex_lib.Point(HEX_SIZE, HEX_SIZE), origin)

    # State
    hex_map = generate_hex_grid(GRID_RADIUS)
    current_type = TYPE_GRASS
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_type = TYPE_GRASS
                elif event.key == pygame.K_2:
                    current_type = TYPE_WATER
                elif event.key == pygame.K_3:
                    current_type = TYPE_DIRT
                elif event.key == pygame.K_4:
                    current_type = TYPE_STONE
                elif event.key == pygame.K_5:
                    current_type = TYPE_SAND
                elif event.key == pygame.K_s:
                    map_lib.save_map("level.map", hex_map)
                elif event.key == pygame.K_l:
                    loaded = map_lib.load_map("level.map")
                    if loaded:
                        hex_map = loaded
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = hex_lib.Point(event.pos[0], event.pos[1])
                    clicked_hex = hex_lib.pixel_to_hex(layout, mouse_pos)
                    if clicked_hex in hex_map:
                        hex_map[clicked_hex] = current_type

        screen.fill(BG_COLOR)

        # Draw Grid
        for h, t in hex_map.items():
            center = hex_lib.hex_to_pixel(layout, h)
            
            # Draw Sprite if available
            sprite = SPRITES.get(t)
            if sprite:
                rect = sprite.get_rect(center=(center.x, center.y))
                screen.blit(sprite, rect)
            else:
                # Fallback to polygon
                corners = hex_lib.polygon_corners(layout, h)
                pixel_corners = [(c.x, c.y) for c in corners]
                color = COLORS.get(t, (255, 255, 255))
                pygame.draw.polygon(screen, color, pixel_corners)
                pygame.draw.polygon(screen, HEX_BORDER_COLOR, pixel_corners, 1)

        # Draw UI (Current Color Indicator)
        # Show sprite or color
        sprite = SPRITES.get(current_type)
        if sprite:
            rect = sprite.get_rect(topleft=(10, 10))
            screen.blit(sprite, rect)
        else:
            pygame.draw.rect(screen, COLORS[current_type], (10, 10, 50, 50))
        
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 50, 50), 2)
        
        # Legend
        font = pygame.font.SysFont("Arial", 16)
        text = font.render(f"Selected: {current_type}", True, (255, 255, 255))
        screen.blit(text, (70, 25))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
