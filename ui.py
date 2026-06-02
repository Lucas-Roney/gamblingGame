import pygame
from settings import *
from buttons import Button

def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(FONT_NAME, size)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)

def draw_text_outline_shadow(
    surface, text, size, x, y,
    text_color,
    outline_color=(0, 0, 0),
    shadow_color=(0, 0, 0),
    outline_width=3,
    shadow_offset=15
):
    font = pygame.font.Font(TITLE_FONT, size)

    # --- Drop Shadow ---
    shadow_surf = font.render(text, True, shadow_color)
    shadow_surf.set_alpha(150)
    shadow_rect = shadow_surf.get_rect(center=(x + shadow_offset, y + shadow_offset))
    surface.blit(shadow_surf, shadow_rect)

    # --- Outline ---
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            outline_surf = font.render(text, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(x + dx, y + dy))
            surface.blit(outline_surf, outline_rect)

    # --- Main Text ---
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)

class Card:
    def __init__(self, image_path, w=150, h=220, rounded=20):
        self.w = w
        self.h = h
        self.rounded = rounded

        # Load and scale
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))

        # Rounded mask
        self.mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.mask, (255, 255, 255), (0, 0, w, h), border_radius=rounded)

    def draw(self, surface, x, y):
        # Apply mask
        card = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        card.blit(self.image, (0, 0))
        card.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(card, (x, y))

class Chip:
    def __init__(self, image_path, value, size=100):
        self.value = value
        self.size = size

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))

    def draw(self, surface, x, y, glow=False):
        if glow:
            glow_rect = pygame.Rect(x-5, y-5, self.size+10, self.size+10)
            pygame.draw.ellipse(surface, (255, 215, 0), glow_rect, width=4)

        surface.blit(self.image, (x, y))

class ShopItem:
    def __init__(self, x, y, w, h, image, label, price):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.transform.scale(image, (w, h))
        self.label = label
        self.price = price
        self.hovered = False

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse)

        # Dark overlay
        item = self.image.copy()
        if not self.hovered:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            item.blit(overlay, (0, 0))

        # Glow
        if self.hovered:
            glow_rect = self.rect.inflate(10, 10)
            pygame.draw.rect(surface, (255, 215, 0), glow_rect, width=4, border_radius=12)

        # Draw item
        surface.blit(item, self.rect)

        # Label
        draw_text_outline_shadow(surface, self.label, 28, self.rect.centerx, self.rect.bottom + 20)

        # Price
        draw_text_outline_shadow(surface, f"{self.price} chips", 24, self.rect.centerx, self.rect.bottom + 50)

class PopupWindow:
    def __init__(self, game, width, height, title, lines):
        self.game = game
        self.width = width
        self.height = height
        self.title = title
        self.lines = lines  # list of strings

        # Centered position
        self.x = (game.WIDTH - width) // 2
        self.y = (game.HEIGHT - height) // 2

        # Play button inside popup
        self.play_button = Button(
            self.x + width//2 - 100,
            self.y + height - 80,
            200,
            50,
            "Play"
        )
        
        # Font
        self.font = pygame.font.Font(RULE_FONT, 22)
        self.title_font = pygame.font.Font(RULE_FONT, 40)


    def draw(self, surface, background):
        # Draw the GAME_SELECT background behind popup
        surface.blit(background, (0, 0))

        # Transparent black rounded rectangle directly on the main surface
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Create a transparent surface for the rounded rect
        rounded = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(
            rounded,
            (0, 0, 0, 180),  # transparent black
            (0, 0, self.width, self.height),
            border_radius=20
        )

        # Blit the transparent rounded rectangle
        surface.blit(rounded, (self.x, self.y))

        # Draw white outline on top
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            bg_rect,
            width=4,
            border_radius=20
        )


        # Title
        draw_text_outline_shadow(
            surface,
            self.title,
            48,
            self.x + self.width//2,
            self.y + 60,
            text_color=(255, 255, 255),
            outline_color=(0, 0, 0),
            shadow_color=(0, 0, 0),
            outline_width=3,
            shadow_offset=4
        )

        # Body text
        y_offset = self.y + 130
        for line in self.lines:
            draw_rule_text(
                surface,
                line,
                self.font,
                self.x + self.width//2,
                y_offset
            )

            y_offset += 40

        # Play button
        self.play_button.draw(surface)

    def is_play_clicked(self):
        return self.play_button.is_clicked()
    
def draw_rule_text(surface, text, font, x, y, color=(255, 255, 255)):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)
